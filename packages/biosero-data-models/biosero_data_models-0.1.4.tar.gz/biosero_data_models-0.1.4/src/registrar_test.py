from biosero.datamodels.adapter import TemplateRegistrar

action_templates = None

td = TemplateRegistrar("http://10.0.0.234:30081", action_templates)

td.register_adapter("TEST-ADAPTER-1", "Test Adapter 1")