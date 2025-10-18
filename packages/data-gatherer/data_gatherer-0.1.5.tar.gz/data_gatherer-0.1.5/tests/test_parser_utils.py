import re
import pandas as pd
from data_gatherer.parser.base_parser import LLMParser
from data_gatherer.parser.xml_parser import XMLParser, XMLRouter, TEI_XMLParser
from data_gatherer.parser.html_parser import HTMLParser
from data_gatherer.parser.pdf_parser import PDFParser
from data_gatherer.parser.grobid_pdf_parser import GrobidPDFParser
from data_gatherer.logger_setup import setup_logging
from conftest import get_test_data_path
from lxml import etree
import requests
import pytest
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# To see logs in the test output, configure the logger to also log to the console (StreamHandler), or set log_file=None in setup_logging.

def test_get_data_availability_elements_from_HTML(get_test_data_path):
    logger = setup_logging("test_logger", log_file="logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_1.html'), 'rb') as f:
        raw_html = f.read()
    preprocessed_data = parser.normalize_HTML(raw_html)
    DAS_elements = parser.retriever.get_data_availability_elements_from_webpage(preprocessed_data)
    print(f"DAS_elements: \n\n{DAS_elements}\n\n")
    assert isinstance(DAS_elements, list)
    assert len(DAS_elements) == 3
    assert all(isinstance(sm, dict) for sm in DAS_elements)
    print('\n')

def test_extract_href_from_supplementary_material_html(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_2.html'), 'rb') as f:
        raw_html = f.read()
    parser.publisher = "PMC"
    hrefs = parser.extract_href_from_supplementary_material(raw_html,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC8628860/")
    print(f"hrefs: \n\n{hrefs.columns}\n\n")
    for col in hrefs.columns:
        if col == 'description':
            print(f"{col}: {hrefs[col].tolist()}")

    assert isinstance(hrefs, pd.DataFrame)
    assert len(hrefs) == 58
    print('\n')

def test_extract_supplementary_material_refs_html(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_2.html'), 'rb') as f:
        raw_html = f.read()
    parser.publisher = "PMC"
    hrefs = parser.extract_href_from_supplementary_material(raw_html,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC8628860/")
    metadata = parser.extract_supplementary_material_refs(raw_html, hrefs)

    expected_len_descriptions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 23665, 1287, 554, 1636, 287, 0, 572, 185, 317, 481,
                                 880, 834, 341, 504, 1412, 615, 630, 440, 491, 1084, 576, 0, 0, 576, 286, 181, 2202, 0,
                                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 33]

    len_descriptions = [len(desc) for desc in metadata['context_description'].tolist()]

    assert isinstance(metadata, pd.DataFrame)
    assert len(metadata) == 58
    assert len_descriptions == expected_len_descriptions

    print('\n')
def test_extract_href_from_supplementary_material_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_2.xml'), 'rb') as f:
        api_xml = f.read()
    parser.publisher = "PMC"
    api_xml = etree.fromstring(api_xml)
    hrefs = parser.extract_href_from_supplementary_material(api_xml,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC11129317/")
    print(f"hrefs: \n\n{hrefs.columns}\n\n")
    print(f"hrefs: \n\n{hrefs['description'].tolist()}\n\n")

    assert isinstance(hrefs, pd.DataFrame)
    assert len(hrefs) == 10
    print('\n')

def test_extract_supplementary_material_refs_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_2.xml'), 'rb') as f:
        api_xml = f.read()
    parser.publisher = "PMC"
    api_xml = etree.fromstring(api_xml)

    hrefs = parser.extract_href_from_supplementary_material(api_xml,
                                                                 "https://pmc.ncbi.nlm.nih.gov/articles/PMC11129317/")
    metadata = parser.extract_supplementary_material_refs(api_xml, hrefs)

    expected_len_descriptions = [9086, 728, 163, 389, 400, 177, 405, 209, 147, 0]

    len_descriptions = [len(desc) for desc in metadata['context_description'].tolist()]

    assert isinstance(metadata, pd.DataFrame)
    assert len(metadata) == 10
    assert len_descriptions == expected_len_descriptions

    print('\n')

def test_extract_paragraphs_from_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_1.xml'), 'rb') as f:  # ✅ open in binary mode
        xml_root = etree.fromstring(f.read())
    paragraphs = parser.extract_paragraphs_from_xml(xml_root)
    assert isinstance(paragraphs, list)
    assert len(paragraphs) > 0
    assert all(isinstance(p, dict) for p in paragraphs)
    print('\n')

def test_extract_sections_from_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_1.xml'), 'rb') as f:  # ✅ open in binary mode
        xml_root = etree.fromstring(f.read())
    section = parser.extract_sections_from_xml(xml_root)
    assert isinstance(section, list)
    assert len(section) > 0
    assert all(isinstance(s, dict) for s in section)
    print('\n')

def test_extract_sections_from_text(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = PDFParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    text = parser.extract_text_from_pdf(get_test_data_path('test_pdf_extract_1.pdf'))
    normalized_text = parser.normalize_extracted_text(text)
    sections = parser.extract_sections_from_text(normalized_text)
    assert isinstance(sections, list)
    assert len(sections) > 0 and len(sections) < 200
    assert all(isinstance(s, dict) for s in sections)
    print('\n')

def test_split_references_from_text(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = PDFParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    text = parser.extract_text_from_pdf(get_test_data_path('test_pdf_refs_1.pdf'))
    normalized_text = parser.normalize_extracted_text(text)
    sections = parser.extract_sections_from_text(normalized_text)
    references = [sections[i] for i in range(len(sections)) if sections[i]['section_title'].startswith("Ref")]
    print(f"references (len {len(references)}): \n\n{references}\n\n")
    assert isinstance(references, list)
    assert len(references) > 0 and len(references) < 200
    assert all(isinstance(r, dict) for r in references)
    print('\n')

def test_resolve_data_repository():
    logger = setup_logging("test_logger", log_file="../logs/scraper.log", level="INFO",
                                    clear_previous_logs=True)
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    test_cases = [
        {
            "extracted_name": "NCBI GEO",
            "target_name": "GEO",
            "extracted_id": "GSE123456"
        },
        {
            "extracted_name": "NCBI Gene Expression Omnibus (GEO)",
            "target_name": "GEO",
            "extracted_id": "GSE923456"
        }
    ]
    for obj in test_cases:
        repo, tgt, extracted_id = obj["extracted_name"], obj["target_name"], obj["extracted_id"]
        print(f"Testing URL: {repo}")
        data_repo = parser.resolve_data_repository(repo, identifier=extracted_id)
        assert isinstance(data_repo, str)
        assert data_repo.lower() == tgt.lower()
        print('\n')

def test_extract_title_from_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, log_file_override=None,
                       llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_1.xml'), 'rb') as f:  # ✅ open in binary mode
        xml_root = etree.fromstring(f.read())
    title = parser.extract_publication_title(xml_root)
    assert isinstance(title, str)
    assert len(title) > 0
    assert title == "Dual molecule targeting HDAC6 leads to intratumoral CD4+ cytotoxic lymphocytes recruitment through MHC-II upregulation on lung cancer cells"
    print('\n')

def grobid_is_alive(grobid_url="http://localhost:8070/api/isalive"):
    try:
        r = requests.get(grobid_url, timeout=2)
        return r.status_code == 200
    except Exception:
        return False

@pytest.mark.skipif(not grobid_is_alive(), reason="GROBID server is not running")
def test_extract_publication_title_GrobidPDFParser(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = GrobidPDFParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    raw_text = parser.extract_full_text_xml(get_test_data_path('test_pdf_refs_1.pdf'))
    router = XMLRouter("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    xml_parser = router.get_parser(raw_text)
    assert isinstance(xml_parser, TEI_XMLParser)
    root = etree.fromstring(raw_text.encode('utf-8'))
    title = xml_parser.extract_publication_title(root)
    assert isinstance(title, str)
    assert len(title) > 0
    assert title == "Pipefish embryo oxygenation, survival, and development: egg size, male size, and temperature effects"


def test_extract_title_from_html_PMC(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_extract_1.html'), 'rb') as f:
        raw_html = f.read()
    title = parser.extract_publication_title(raw_html)
    assert isinstance(title, str)
    assert len(title) > 0
    assert "Proteogenomic insights suggest druggable pathways in endometrial carcinoma" in title
    print('\n')

def test_extract_title_from_html_nature(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('Webscraper_fetch_1.html'), 'rb') as f:
        raw_html = f.read()
    title = parser.extract_publication_title(raw_html)
    assert isinstance(title, str)
    assert "Defective N-glycosylation of IL6 induces metastasis and tyrosine kinase inhibitor resistance" in title
    print('\n')

def test_semantic_retrieve_from_corpus(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log", level=logging.INFO)
    parser = HTMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('Webscraper_fetch_1.html'), 'rb') as f:
        raw_html = f.read()
    corpus = parser.extract_sections_from_html(raw_html)
    query = "Available data, accession code, data repository, deposited data, obtained data"
    top_k_sections = parser.semantic_retrieve_from_corpus(corpus, topk_docs_to_retrieve=5, query=query)
    accession_ids = ['GSE269782', 'GSE31210', 'GSE106765', 'GSE60189', 'GSE59239', 'GSE122005', 'GSE38121', 'GSE71587',
                     'GSE37699', 'PXD051771']
    #print(f"top_k_sections: {[sect['L2_distance'] for sect in top_k_sections]}")
    scores = [1.2540757656097412, 1.4350833892822266, 1.4540908336639404, 1.461714744567871, 1.496106505393982]
    DAS_text = ".\n".join([item['text'] for item in top_k_sections])
    assert isinstance(top_k_sections, list)
    assert len(top_k_sections) == 5
    assert all(isinstance(res, dict) for res in top_k_sections)
    for acc_id in accession_ids:
        assert acc_id.lower() in str.lower(DAS_text)
    for sect_i, sect in enumerate(top_k_sections):
        assert abs(sect['L2_distance'] - scores[sect_i]) < 0.05
    print('\n')

def test_normalize_text_from_pdf(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = PDFParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    raw_text = parser.extract_text_from_pdf(get_test_data_path('test_pdf_extract_1.pdf'))
    normalized_text = parser.normalize_extracted_text(raw_text)
    assert isinstance(normalized_text, str)
    assert len(normalized_text) > 0
    assert len(normalized_text) < 178720
    assert not re.search('\nPage\s+\d+\s*', normalized_text)
    assert not re.search('\nNewpage\s+\d+\s*', normalized_text)
    print('\n')

def test_safe_parse_json(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    malformed_json = """
    {"datasets":[{"dataset_identifier":"GSE39582","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE39582"},{"dataset_identifier":"GSE13067","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE13067"},{"dataset_identifier":"GSE13294","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE13294"},{"dataset_identifier":"GSE14333","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE14333"},{"dataset_identifier":"GSE17536","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE17536"},{"dataset_identifier":"GSE33113","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE33113"},{"dataset_identifier":"GSE37892","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE37892"},{"dataset_identifier":"GSE38832","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE38832"},{"dataset_identifier":"PRJEB23709","repository_reference":"https://www.ncbi.nlm.nih.gov/bioproject/PRJEB23709"},{"dataset_identifier":"GSE103479","repository_reference":"https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE103479"},{"
    """
    parsed_data = parser.llm_client.safe_parse_json(malformed_json)
    dada = parsed_data["datasets"]

    print(f"parsed_data:\nType:{type(parsed_data)}\nLen:{len(dada)},Cont: {parsed_data}\n")
    assert isinstance(parsed_data, dict)
    assert len(parsed_data["datasets"]) == 10  # Only 10 complete entries should be parsed
    print('\n')

def test_is_tei_xml(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    with open(get_test_data_path('test_tei_xml_extract.xml'), 'rb') as f:
        xml_bytes = f.read()
    # Accept both string and etree.Element input for the router/static method
    try:
        xml_root = etree.fromstring(xml_bytes)
    except Exception as e:
        logger.error(f"Failed to parse XML: {e}")
        assert False, "Could not parse test TEI XML file"

    # Use the static method for robust detection
    is_tei = XMLParser.is_tei_xml_static(xml_root)
    assert isinstance(is_tei, bool)
    assert is_tei is True
    print('\n')

def test_schema_validation(get_test_data_path):
    logger = setup_logging("test_logger", log_file="../logs/scraper.log")
    parser = XMLParser("open_bio_data_repos.json", logger, llm_name='gemini-2.0-flash')
    test_cases = [
        {'dataset_id': 'https://doi.org/10.1594/PANGAEA.964081', 'repository_reference': 'PANGAEA'},
        {'dataset_id': 'https://doi.org/10.17632/xtb4mkvf8f.1', 'repository_reference': 'data.mendeley.com'},
        {'dataset_id': 'MSV000081006', 'repository_reference': 'massive.ucsd.edu'}, 
        {'dataset_id': '10.7937/tcia.2019.30ilqfcl', 'repository_reference': 'cancerimagingarchive.net'},
        {'dataset_identifier': 'syn9702085', 'repository_reference': 'https://www.synapse.org/#!Synapse:syn9702085', 'dataset_id': 'syn9702085'},
        {'dataset_identifier': 'M27187', 'repository_reference': 'https://www.ncbi.nlm.nih.gov/nuccore/M27187', 'dataset_id': 'M27187'}
    ]
    ret_cases = [  # change these when adding support for new repos
        {'dataset_identifier': '10.1594/PANGAEA.964081', 'repository_reference': 'doi.org', 'dataset_webpage': 'https://doi.pangaea.de/10.1594/PANGAEA.964081'}, 
        {'dataset_identifier': '10.17632/xtb4mkvf8f.1', 'repository_reference': 'data.mendeley.com', 'dataset_webpage': 'https://data.mendeley.com/datasets/xtb4mkvf8f/1'},
        {'dataset_identifier': 'MSV000081006', 'repository_reference': 'massive.ucsd.edu'},
        {'dataset_identifier': '10.7937/tcia.2019.30ilqfcl', 'repository_reference': 'cancerimagingarchive.net', 'dataset_webpage': 'https://www.cancerimagingarchive.net/collection/acrin-nsclc-fdg-pet/'},
        {'dataset_identifier': 'syn9702085', 'repository_reference': 'synapse.org', 'dataset_webpage': 'https://www.synapse.org/#!Synapse:syn9702085'},
        {'dataset_identifier': 'M27187', 'repository_reference': 'nuccore', 'dataset_webpage': 'https://www.ncbi.nlm.nih.gov/nuccore/M27187'}
    ]
    for obj,ret in zip(test_cases, ret_cases):
        dataset_id_val, data_repo_val, dataset_webpage_val = parser.schema_validation(obj, req_timeout=5)
        print(f"Testing dataset_id_val: {dataset_id_val}, data_repo_val: {data_repo_val}, dataset_webpage_val: {dataset_webpage_val}\n")
        assert isinstance(dataset_id_val, str)
        assert isinstance(data_repo_val, str)
        assert isinstance(dataset_webpage_val, str) or dataset_webpage_val is None
        assert dataset_id_val == ret['dataset_identifier']
        assert data_repo_val.lower() == ret['repository_reference'].lower()
        assert dataset_webpage_val == ret['dataset_webpage'] if 'dataset_webpage' in ret else dataset_webpage_val is None
        print('\n')
        