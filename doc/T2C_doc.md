#Table To Conversation T2C#

T2C is XLSX (MS Excell) based format for fast authoring of conversations in spreadsheets. Detailed description is in  [../examples/cz_app/xls/E_EN_T2C_authoring.xlsx](../examples/en_app/xls/E_EN_T2C_authoring.xlsx)


##Examples of mapping T2C, XML and JSON##
We provide here some examples to illustrate how WAW T2C, WAW XML and WA JSON map in particular use cases.

### Buttons ###

**WAW T2C format** (column B, we omit %%b if putting it to column C)

    %%bHospital=moved to hospital;released soon= the patient will be released from hospital soon
 
**WAW XML format**
	
    <output>
      <generic structure="listItem">
        <response_type>option</response_type>
        <preference>button</preference>
        <title>Fast selection buttons</title>
        <options>
          <label>teď byl převezen</label>
          <value>
            <input>
              <text>teď byl převezen do nemocnice</text>
            </input>
          </value>
        </options>
        <options>
          <label>brzy propustí</label>
          <value>
            <input>
              <text>pacienta brzy propustí z nemocnice</text>
            </input>
          </value>
        </options>
      </generic>
      ....
    </output>

	

**WA JSON**

    "output": {
        "generic": [
            {
                "title": "Fast selection buttons", 
                "response_type": "option", 
                "preference": "button", 
                "options": [
                    {
                        "value": {
                            "input": {
                                "text": "teď byl převezen do nemocnice"
                            }
                        }, 
                        "label": "teď byl převezen"
                    }, 
                    {
                        "value": {
                            "input": {
                                "text": "pacienta brzy propustí z nemocnice"
                            }
                        }, 
                        "label": "brzy propustí"
                    }
                ]
            }
        ], 
        "text": { ....
