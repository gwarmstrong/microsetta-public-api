import json
from pkg_resources import resource_filename
from microsetta_public_api import config
from microsetta_public_api.resources import resources

import connexion
from flask import render_template


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

    @app.route('/demos/percentiles-plot/')
    def percentiles_plot():
        return render_template('percentiles-plot.html')

    @app.route('/demos/data-table')
    def data_table_demo():
        return render_template('data-table.html')

    @app.route('/demos/participant-interface/')
    def participant_interface_enter_id():
        return render_template('participant-interface-start.html')

    @app.route('/demos/participant-interface/<uid>')
    def participant_interface(uid):
        return render_template('participant-interface-concrete.html',
                               sample_id=uid)

    return app


if __name__ == "__main__":
    import sys

    config_fp = sys.argv[1] if len(sys.argv) > 1 else None
    if config_fp:
        app = build_app(resources_config_json=config_fp)
        app.run(port=8083, debug=True)
    else:
        # import TestDatabase here to avoid circular import
        from microsetta_public_api.utils.testing import TestDatabase
        with TestDatabase():
            app = build_app()
            app.run(port=8083, debug=True)
