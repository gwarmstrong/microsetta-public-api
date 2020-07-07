import json
from pkg_resources import resource_filename
from microsetta_public_api import config
from microsetta_public_api.resources import resources
from flask import render_template

import connexion


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

    @app.route('/demos/data-table')
    def data_table_demo():
        return render_template('data-table.html')

    return app


if __name__ == "__main__":
    import sys
    config_fp = sys.argv[1] if len(sys.argv) > 1 else None
    app = build_app(resources_config_json=config_fp)
    app.run(port=8083, debug=True)
