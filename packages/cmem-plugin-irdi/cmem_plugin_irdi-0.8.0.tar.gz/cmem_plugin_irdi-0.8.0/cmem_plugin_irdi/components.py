"""PluginParameters and validation regex's for IRDI components"""

from cmem_plugin_base.dataintegration.description import PluginParameter

components = {
    "icd": {
        "parameter": PluginParameter(
            name="icd", label="International Code Designator (ICD): Numeric, 4 characters"
        ),
        "regex": r"^\d{4}$",
    },
    "oi": {
        "parameter": PluginParameter(
            name="oi",
            label="Organization Identifier (OI): Numeric, 4 characters",
        ),
        "regex": r"^\d{4}$",
    },
    "opi": {
        "parameter": PluginParameter(
            name="opi",
            label="Organization Part Identifier (OPI): Alphanumeric, up to 35 characters (base36)",
            default_value="",
        ),
        "regex": r"^[a-zA-Z0-9]{0,35}$",
    },
    "opis": {
        "parameter": PluginParameter(
            name="opis",
            label="OPI Source Indicator (OPIS): Numeric, 1 character",
            default_value="",
        ),
        "regex": r"^\d$",
    },
    "ai": {
        "parameter": PluginParameter(
            name="ai",
            label="Additional information (AI): Numeric, 4 characters",
            default_value="",
        ),
        "regex": r"^\d{4}$",
    },
    "csi": {
        "parameter": PluginParameter(
            name="csi",
            label="Code-space identifier (CSI): Alphanumeric, 2 character (base36)",
        ),
        "regex": r"^[a-zA-Z0-9]{2}$",
    },
}
