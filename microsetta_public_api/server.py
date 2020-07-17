import json
from flask import jsonify
from pkg_resources import resource_filename
from microsetta_public_api import config
from microsetta_public_api.resources import resources
from microsetta_public_api.exceptions import UnknownID

import connexion


def handle_unknown_id(e: UnknownID):
    return jsonify(missing_ids=e.missing_ids,
                   error=404, text=f"Sample ID(s) not found for "
                                   f"{e.type_}: {e.value}"), \
            404


def build_app(resources_config_json=None):
    app = connexion.FlaskApp(__name__)

    # default configuration for resources is provided in
    # microsetta.config.resources, this config can be updated by a json file
    # passed to `build_app`.
    if resources_config_json is not None:
        with open(resources_config_json) as fp:
            resource_updates = json.load(fp)
        config.resources.update(resource_updates)

        resources.update(config.resources)

    app_file = resource_filename('microsetta_public_api.api',
                                 'microsetta_public_api.yml')
    app.add_api(app_file, validate_responses=True)

    app.app.register_error_handler(UnknownID, handle_unknown_id)

    return app


if __name__ == "__main__":
    import sys
    config_fp = sys.argv[1] if len(sys.argv) > 1 else None
    app = build_app(resources_config_json=config_fp)
    app.run(port=8083, debug=True)
