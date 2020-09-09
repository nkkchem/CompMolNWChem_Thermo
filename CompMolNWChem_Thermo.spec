/*
A KBase module: CompMolNWChem_Thermo
*/

module CompMolNWChem_Thermo {
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    /*
        This example function accepts any number of parameters and returns results in a KBaseReport
    */
    funcdef run_CompMolNWChem_Thermo(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;

};
