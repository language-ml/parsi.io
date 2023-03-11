import os
import logging

resource_path = os.path.join("parsi_io", "resources")
if not os.path.exists(resource_path):
    logging.warning("resources directory does not exist! Most modules need resources in this directory.")

chunker_path = os.path.join(resource_path, "chunker.model")
if not os.path.exists(resource_path):
    logging.warning("chunker model does not exist!")

postagger_path = os.path.join(resource_path, "postagger.model")
if not os.path.exists(resource_path):
    logging.warning("postagger model does not exist!")