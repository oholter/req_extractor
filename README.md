# req_extractor
Code to parse requrement PDF documents and extract requirement sentences with context.

## Parse PDF documents
Edit the java-file: ``pdf_parser/src/main/java/req_extract/PDFParser.java``.
In the main method change:
* documentCode
* pdfPath
* outPath
* the page number of the last page
* theme
* edition

In the parseRequirement method, change the flags to fit the structure of the current document.

### Compile and run the java code:
1. Install java and maven
2. Enter the pdf_parser folder  
``cd pdf_parser``
3. Compile and execute  
``mvn clean compile exec:java``
4. Confirm that the XML file is a valid XML. Note: You may have to manually correct some mistakes in the XML file.





## Extract requirement sentences

### Setup execution environment
1. Create and enter a virtual environment  
``python -m venv venv``  
``source ./venv/bin/activate``

2. Install dependencies:  
``python -m pip install -r requirements.txt``  
``python -m spacy download en_core_web_sm``

### Convert the extracted XML to a JSON file with requirement sentences

1. Ensure the input/output are correct and change other options in ``req_extract/config.cfg``

2. Convert the document structure from XML to JSON:  
``python -m req_extract.xml2json INPUT``

3. To convert from document type JSON to sentence requirement sentence style JSON:  
``python -m req_extract.json2json INPUT``


### Sample requirements

* To sample 100 sentences from a document
(samples n random unique samples from the document, order is random)  
``python -m utils.sample_requirements INPUT [-n 100]``

You would then have a number of documents with n sentences in each.

Manually concatenate them...

### Shuffle the order of the requirements

* To shuffle the order of a document with sentence:  
``python -m utils.shuffle_req INPUT``


### Divide the JSON file into multiple JSON files

* To divide a JSON document in 20 documents with the same number of sentences:  
``python -m utils.divide_json_document INPUT [-n 20]``


### Transform the JSON file into a JSONL file  
``python -m utils.json2jsonl INPUT``
