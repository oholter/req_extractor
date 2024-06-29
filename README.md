# req_extractor
Code to parse requrement PDF documents and extract requirement sentences with context.

## Parse PDF documents
Edit the java-file: ``pdf_parser/src/main/java/req_extract/PDFParser.java``  
In the main method change:
* DocumentCode
* pdfPath
* outPath
* the page number of the last page
* Theme and edition

In the parseRequirement method, change the flags depending on structure of the document.

### Compile and run java-code:
1. Install maven
2. Enter the pdf_parser folder ``cd pdf_parser``
3. Compile and execute ``mvn compile exec:java``
4. Confirm that the XML file is a valid XML. Note: You may have to manually correct some mistakes in the XML file.





## Extract requirement sentences

Change the input/output directories and other options in ``req_extract/config.cfg``

To convert the document structure from XML to JSON:
``python3 -m req_extract.xml2json INPUT``

To convert from document type json to sentence style json:
``python3 -m req_extract.json2json INPUT``

To sample 100 sentences from a document
(samples n random unique samples from the document, order is random)
``python3 -m utils.sample_requirements INPUT [-n 100]``

You would then have a number of documents with n sentences in each.

Manually concatenate them...

To shuffle the order of a document with sentence
``python3 -m utils.shuffle_req INPUT``

To divide a json document in 20 documents with the same number of sentences:
``python3 -m src.divide_json_document INPUT [-n 20]``
