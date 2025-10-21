import os
from sparknlp.pretrained import PretrainedPipeline
from johnsnowlabs import nlp

nlp.install(
    browser_login=False,
    force_browser=False,
    hardware_platform="cpu",
)

spark = nlp.start()
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
spark.sparkContext.setLogLevel("ERROR")
deid_pipeline = PretrainedPipeline(
    "clinical_deidentification_docwise_wip", "de", "clinical/models"
)



import os
import logging
import json
from typing import List
from mlflow.johnsnowlabs import JSLPythonModel
from sparknlp.pretrained import PretrainedPipeline
from johnsnowlabs import nlp


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClinicalDeidentification(JSLPythonModel):
    """
    Clinical Deidentification model inheriting from JSLPythonModel.
    """

    ALLOWED_MASKING_POLICIES = ["masked", "obfuscated"]

    def __getstate__(self):
        """Exclude Spark and pipeline objects from pickling"""
        state = self.__dict__.copy()
        state["spark"] = None
        state["spark_model"] = None
        return state

    def __setstate__(self, state):
        """Restore state"""
        self.__dict__.update(state)

    def load_context(self, context):
        """
        Load the model and initialize Spark context.
        This method is called when the model is loaded from MLflow.
        """
        self.has_error = False
        self.error_message = ""

        logger.info("Loading ClinicalDeidentification model...")

        try:
            model_path = context.artifacts.get("model")

            if self.spark is None:
                from mlflow.johnsnowlabs import _get_or_create_sparksession

                self.spark = _get_or_create_sparksession(model_path)
                logger.info("Spark session initialized")

            if self.spark_model is None:
                from sparknlp.pretrained import PretrainedPipeline

                self.spark_model = PretrainedPipeline.from_disk(model_path)
                logger.info("Pretrained pipeline loaded successfully")
        except Exception as e:
            self.error_message = f"Failed to load model: {str(e)}"
            self.has_error = True
            logger.error(self.error_message)
            raise

    def _create_error_response(self, error_message):
        """Create a standardized error response"""
        return [f"Error: {str(error_message)}"]

    def _validate_masking_policy(self, masking_policy: str) -> None:
        """
        Validate that the masking_policy is one of the allowed values.

        Args:
            masking_policy: The masking policy to validate

        Raises:
            ValueError: If masking_policy is not in ALLOWED_MASKING_POLICIES
        """
        if masking_policy not in self.ALLOWED_MASKING_POLICIES:
            raise ValueError(
                f"Invalid masking_policy: '{masking_policy}'. "
                f"Allowed values are: {self.ALLOWED_MASKING_POLICIES}"
            )

    def get_attr_or_key(self, item, key):
        """Fetches an attribute or dictionary key from an item."""
        return getattr(item, key, None) if hasattr(item, key) else item.get(key, None)

    def prepare_payload(self, deid_res, text: str):
        sentences = deid_res["document"]
        obfuscateds = deid_res["obfuscated"]
        mask_entities = deid_res["masked"]
        sentence_begin = 0
        obfuscated_str = ""
        masked_str = ""

        for index, sent in enumerate(sentences):
            begin = self.get_attr_or_key(sent, "begin")
            end = self.get_attr_or_key(sent, "end")
            obfuscated_result = self.get_attr_or_key(obfuscateds[index], "result")
            mask_entity_result = self.get_attr_or_key(mask_entities[index], "result")

            # Build the obfuscated and masked strings
            obfuscated_str += text[sentence_begin:begin] + obfuscated_result
            masked_str += text[sentence_begin:begin] + mask_entity_result
            sentence_begin = end + 1

        return {
            "masked": masked_str,
            "obfuscated": obfuscated_str,
        }

    def process_deid_results(
        self, deid_res: list, masking_policy: List, texts: list
    ) -> list:
        return [
            self.prepare_payload(res, text)[policy]
            for res, text, policy in zip(deid_res, texts, masking_policy)
        ]

    def get_predictions_from_light_pipeline(self, texts: list) -> list:
        logger.debug(f"Processing {len(texts)} texts with Light Pipeline")
        return self.spark_model.fullAnnotate(texts)

    def get_predictions_from_pretrained_pipeline(self, texts: List[str]) -> list:

        logger.debug(f"Processing {len(texts)} texts with Pretrained Pipeline")
        input_df = self.prepare_data(texts)
        predictions_df = self.spark_model.transform(input_df)
        sorted_df = predictions_df.orderBy("index")
        logger.debug("Transformation complete, extracting results")

        output_df = sorted_df.select(
            "document",
            "masked", 
            "obfuscated"
        )

        json_result = output_df.toJSON().collect()
        predictions_list = list(map(json.loads, json_result))

        return predictions_list

    def prepare_data(self, texts: List[str]):
        logger.debug("Preparing the Spark DataFrame")
        indexed_text = [(i, t) for i, t in enumerate(texts)]
        df = self.spark.createDataFrame(indexed_text, ["index", "text"])
        return df.repartition(1000)

    def get_predictions(self, texts: List[str]) -> list:
        if len(texts) < 20:
            return self.get_predictions_from_light_pipeline(texts)
        else:
            return self.get_predictions_from_pretrained_pipeline(texts)

    def predict(self, context, model_input, params=None):
        logger.info(f"Received model input: {model_input}")
        logger.info(f"Received parameters: {params}")
        logger.info(f"Received model input type: {type(model_input)}")

        texts = model_input["text"].iloc[0]
        logger.info(f"Raw texts: {texts}")

        if hasattr(texts, "tolist"):
            logger.info(f"texts is a numpy array: {texts}")
            texts = texts.tolist()
        elif not isinstance(texts, list):
            logger.info(f"texts is not a list: {texts}")
            texts = list(texts)

        if params is None:
            params = {}

        masking_policy = params.get("masking_policy", "masked")

        try:
            self._validate_masking_policy(masking_policy)
        except ValueError as e:
            logger.error(str(e))
            return self._create_error_response(str(e))

        if self.has_error:
            return self._create_error_response(self.error_message)

        try:
            policy_list = [masking_policy] * len(texts)
            results = self.get_predictions(texts)
            predictions = self.process_deid_results(results, policy_list, texts)
            return predictions
        except Exception as e:
            error_message = f"Prediction failed: {str(e)}"
            logger.error(error_message)
            return self._create_error_response(error_message)

import mlflow

mlflow.set_registry_uri('databricks-uc')
CATALOG = "ml"
SCHEMA = "model"
registered_model_name = f"{CATALOG}.{SCHEMA}.dev_clinical_deidentification_docwise_wip_de"


import pandas as pd
import mlflow
import mlflow.johnsnowlabs
from mlflow.models import infer_signature


def log_model():
    import mlflow.johnsnowlabs
    from mlflow.models import infer_signature

    input_example_1 = {
        "text": [
            """Dr. Hans-Wolfgang Weihmann - RM57, Städt Klinikum Dresden-Friedrichstadt, Friedrichstraße 41, Dresden"""
        ]
    }

    input_example = {"text": ["text document 1", "text document 2"]}

    output_response = {
        "predictions": [
            "Output text document 1",
            "Output text document 2",
        ]
    }

    params = {
        "masking_policy": "masked",
    }

    signature = infer_signature(
        model_input=input_example, model_output=output_response, params=params
    )

    clinical_model = ClinicalDeidentification(
        spark_model=deid_pipeline.model, spark=spark
    )

    # Log using the enhanced johnsnowlabs flavor with python_model
    # First, try logging without registration to avoid timing issues
    try:
        model_info = mlflow.johnsnowlabs.log_model(
            spark_model=clinical_model,
            name='model',
            signature=signature,
            input_example=input_example_1, 
            extra_pip_requirements=[
                "mlflow==3.3.2",
                "cloudpickle==3.1.1",
                "mlflow-by-johnsnowlabs==3.4.1.post1",
            ],
            registered_model_name=None,  # Don't register yet
            await_registration_for=0,
        )
        logger.info(f"Model logged successfully. Model ID: {model_info.model_uuid}")
        
        # Now try to register separately with a small delay to ensure upload completes
        import time
        time.sleep(5)  # Give Databricks time to finalize the upload
        
        try:
            mlflow.register_model(
                f"models:/{model_info.model_uuid}",
                registered_model_name,
                await_registration_for=600,
            )
            logger.info(f"Model registered successfully as {registered_model_name}")
        except Exception as reg_error:
            logger.warning(f"Automatic registration failed: {reg_error}")
            logger.info(f"Model logged but not registered. Register manually using model ID: {model_info.model_uuid}")
        
        return model_info
        
    except Exception as e:
        logger.error(f"Model logging failed completely: {e}")
        raise

import os
import json

# Load the license file content
with open("spark_nlp_for_healthcare_spark_ocr_9968.json") as f:
    license_content = f.read()

os.environ["JOHNSNOWLABS_LICENSE_JSON"] = license_content

os.environ['HEALTHCARE_SECRET'] =  ""

# Disable parallel uploads to avoid "empty parts" error in Databricks
os.environ['DATABRICKS_SDK_UPSTREAM_USE_PARALLEL_UPLOAD'] = 'false'
# Also try disabling mlflowdbfs
os.environ['DISABLE_MLFLOWDBFS'] = 'true'

model_info = log_model()