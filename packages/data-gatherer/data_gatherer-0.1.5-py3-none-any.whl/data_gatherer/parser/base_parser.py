from abc import ABC, abstractmethod
import re
import logging
import pandas as pd
import typing_extensions as typing
from pydantic import BaseModel
import os
import json
from data_gatherer.prompts.prompt_manager import PromptManager
import tiktoken
from data_gatherer.resources_loader import load_config
from data_gatherer.retriever.embeddings_retriever import EmbeddingsRetriever
import requests
from json_repair import repair_json

from data_gatherer.llm.llm_client import LLMClient_dev
from data_gatherer.llm.response_schema import *

# Abstract base class for parsing data
class LLMParser(ABC):
    """
    This class is responsible for parsing data using LLMs. This will be done either:

    - Full Document Read (LLMs that can read the entire document)

    - Retrieve Then Read (LLMs will only read a target section retrieved from the document)
    """

    def __init__(self, open_data_repos_ontology, logger, log_file_override=None, full_document_read=True,
                 prompt_dir="data_gatherer/prompts/prompt_templates",
                 llm_name=None, save_dynamic_prompts=False, save_responses_to_cache=False, use_cached_responses=False,
                 use_portkey=True):
        """
        Initialize the LLMParser with configuration, logger, and optional log file override.

        :param open_data_repos_ontology: Configuration dictionary containing repo info

        :param logger: Logger instance for logging messages.

        :param log_file_override: Optional log file override.
        """
        self.open_data_repos_ontology = load_config(open_data_repos_ontology)

        self.logger = logger
        self.logger.info("LLMParser initialized.")

        self.llm_name = llm_name
        entire_document_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp", "gemini-2.0-flash",
                                  "gemini-2.5-flash", "gpt-4o", "gpt-4o-mini", "gpt-5-nano", "gpt-5-mini", "gpt-5"]

        self.full_document_read = full_document_read and self.llm_name in entire_document_models
        self.title = None
        self.prompt_manager = PromptManager(prompt_dir, self.logger,
                                            save_dynamic_prompts=save_dynamic_prompts,
                                            save_responses_to_cache=save_responses_to_cache,
                                            use_cached_responses=use_cached_responses)
        self.repo_names = self.get_all_repo_names()
        self.repo_domain_to_name_mapping = self.get_repo_domain_to_name_mapping()

        self.save_dynamic_prompts = save_dynamic_prompts
        self.save_responses_to_cache = save_responses_to_cache
        self.use_cached_responses = use_cached_responses

        self.use_portkey = use_portkey
        
        # Initialize unified LLM client for all models
        self.llm_client = LLMClient_dev(
            model=llm_name,
            logger=self.logger,
            use_portkey=use_portkey,
            save_dynamic_prompts=save_dynamic_prompts,
            save_responses_to_cache=save_responses_to_cache,
            use_cached_responses=use_cached_responses,
            prompt_dir=prompt_dir
        )

    # create abstract method for subclasses to implement parse_data
    @abstractmethod
    def parse_data(self, raw_data, current_url):
        """
        Parse the raw data using the configured LLM.

        :param raw_data: The raw data to be parsed (XML or HTML).

        :param current_url: The current URL address being processed.

        :return: Parsed data as a DataFrame or list of dictionaries.
        """
        pass

    def extract_file_extension(self, download_link):
        self.logger.debug(f"Function_call: extract_file_extension({download_link})")
        # Extract the file extension from the download link
        extension = None
        if type(download_link) == str:
            extension = download_link.split('.')[-1]
        if type(extension) == str and ("/" in extension):  # or "?" in extension
            return ""
        return extension

    def load_patterns_for_tgt_section(self, section_name):
        """
        Load the XML tag patterns for the target section from the configuration.

        :param section_name: str — name of the section to load.

        :return: str — XML tag patterns for the target section.
        """

        self.logger.info(f"Function_call: load_patterns_for_tgt_section({section_name})")
        self.logger.info(f"Consider migrating this function to the BaseRetriever class.")
        return self.retriever.load_target_sections_ptrs(section_name)

    def generate_dataset_description(self, data_file):
        # from data file
        # excel, csv, json, xml, etc.
        # autoDDG
        raise NotImplementedError("DDG not implemented yet")

    def reconstruct_download_link(self, href, content_type, current_url_address):
        download_link = None
        self.logger.debug(f"Function_call: reconstruct_download_link({href}, {content_type}, {current_url_address})")
        if self.publisher == 'PMC':
            PMCID = re.search(r'PMC(\d+)', current_url_address, re.IGNORECASE).group(1)
            self.logger.debug(
                f"Inputs to reconstruct_download_link: {href}, {content_type}, {current_url_address}, {PMCID}")
            if content_type == 'local-data':
                download_link = "https://pmc.ncbi.nlm.nih.gov/articles/instance/" + PMCID + '/bin/' + href
            elif content_type == 'media p':
                file_name = os.path.basename(href)
                self.logger.debug(f"Extracted file name: {file_name} from href: {href}")
                download_link = "https://www.ncbi.nlm.nih.gov/pmc" + href

        else:
            self.logger.debug(f"Extracted download_link as href: {href}")
            download_link = href

        return download_link

    def union_additional_data(self, parsed_data, additional_data):
        self.logger.info(f"Merging additional data ({type(additional_data)}) with parsed data({type(parsed_data)}).")
        self.logger.info(f"Additional data\n{additional_data}")
        return pd.concat([parsed_data, additional_data], ignore_index=True)

    def process_additional_data(self, additional_data, prompt_name='GPT_FewShot',
                                response_format=dataset_response_schema_gpt):
        """
        Process the additional data from the webpage. This is the data matched from the HTML with the patterns in
        retrieval_patterns xpaths.

        :param additional_data: List of dictionaries containing additional data to be processed.

        :return: List of dictionaries containing processed data.

        """
        self.logger.info(f"Processing additional data: {len(additional_data)} items")
        repos_elements = []
        for repo, details in self.open_data_repos_ontology['repos'].items():
            entry = repo
            if 'repo_name' in details:
                entry += f" ({details['repo_name']})"
            repos_elements.append(entry)

        # Join the elements into a properly formatted string
        repos = ', '.join(repos_elements)

        # Log for debugging
        self.logger.info(f"Repos elements: {repos_elements}")

        ret = []
        for element in additional_data:
            self.logger.info(f"Processing additional data element ({type(element)}): {element}")
            cont = element['surrounding_text']

            if 'Supplementary Material' in cont or 'supplementary material' in cont:
                continue

            if (element['source_section'] in ['data availability', 'data_availability', 'data_availability_elements']
                or 'data availability' in cont) and len(cont) > 1:
                self.logger.info(f"Processing data availability text")
                # Call the generalized function
                datasets = self.extract_datasets_info_from_content(
                    cont, 
                    repos_elements, model=self.llm_name,
                    temperature=0,
                    prompt_name=prompt_name,
                    response_format=response_format
                )

                for dt in datasets:
                    dt['source_section'] = element['source_section']
                    dt['retrieval_pattern'] = element['retrieval_pattern']

                ret.extend(datasets)
            else:
                self.logger.debug(f"Processing supplementary material element")
                ret.append(element)

        self.logger.info(f"Final ret additional data: {len(ret)} items")
        self.logger.debug(f"Final ret additional data: {ret}")
        return ret

    def process_data_availability_text(self, DAS_content, prompt_name='GPT_FewShot',
                                       response_format=dataset_response_schema_gpt):
        """
        Process the data availability section from the webpage.

        :param DAS_content: list of all text content matching the data availability section patterns.

        :return: List of dictionaries containing processed data.
        """
        self.logger.info(f"Processing DAS_content: {len(DAS_content)} elements")
        repos_elements = self.repo_names

        # Call the generalized function
        datasets = []
        for element in DAS_content:
            datasets.extend(self.extract_datasets_info_from_content(element, repos_elements,
                                                                    model=self.llm_name,
                                                                    temperature=0,
                                                                    prompt_name=prompt_name,
                                                                    response_format=response_format))

        # Add source_section information and return
        ret = []
        self.logger.info(f"datasets ({type(datasets)}): {datasets}")
        for dataset in datasets:
            self.logger.info(f"iter dataset ({type(dataset)}): {dataset}")
            dataset['source_section'] = 'data_availability'
            self.logger.warning(f"Adding retrieval pattern 'data availability' to dataset")
            dataset['retrieval_pattern'] = 'data availability'
            ret.append(dataset)

        self.logger.info(f"Final ret data availability: {len(ret)} items")
        self.logger.info(f"Final ret data availability: {ret}")
        return ret

    def extract_datasets_info_from_content(self, content: str, repos: list, model: str = 'gpt-4o-mini',
                                           temperature: float = 0.0,
                                           prompt_name: str = 'GPT_FewShot',
                                           full_document_read=True,
                                           response_format = dataset_response_schema_gpt) -> list:
        """
        Extract datasets from the given content using a specified LLM model.
        Uses a static prompt template and dynamically injects the required content.
        It also performs token counting and llm response normalization.

        :param content: The content to be processed.

        :param repos: List of repositories to be included in the prompt.

        :param model: The LLM model to be used for processing.

        :param temperature: The temperature setting for the model.

        :return: List of datasets retrieved from the content.
        """
        self.logger.info(f"Function_call: extract_datasets_info_from_content(...)")
        self.logger.debug(f"Loading prompt: {prompt_name} for model {model}")
        static_prompt = self.prompt_manager.load_prompt(prompt_name)
        n_tokens_static_prompt = self.count_tokens(static_prompt, model)

        if 'gpt' in model:
            while self.tokens_over_limit(content, model, allowance_static_prompt=n_tokens_static_prompt):
                content = content[:-2000]
        self.logger.info(f"Content length: {len(content)}")

        if 'gemma' in model or 'qwen' in model:
            if self.tokens_over_limit(content, model, allowance_static_prompt=n_tokens_static_prompt, limit=32000):
                self.logger.warning(f"Content length {len(content)} exceeds the model's token limit. "
                                    f"Truncating content to fit within the limit.")
                content = content[:-2000]

        self.logger.debug(f"static_prompt: {static_prompt}")

        # Render the prompt with dynamic content
        messages = self.prompt_manager.render_prompt(
            static_prompt,
            entire_doc=self.full_document_read,
            content=content,
            repos=', '.join(repos)
        )
        self.logger.info(f"Prompt messages total length: {self.count_tokens(messages, model)} tokens")
        self.logger.debug(f"Prompt messages: {messages}")

        # Generate the checksum for the prompt content
        # Save the prompt and calculate checksum
        prompt_id = f"{model}-{temperature}-{self.prompt_manager._calculate_checksum(str(messages))}"
        self.logger.info(f"Prompt ID: {prompt_id}")
        # Save the prompt using the PromptManager
        if self.save_dynamic_prompts:
            self.prompt_manager.save_prompt(prompt_id=prompt_id, prompt_content=messages)

        if self.use_cached_responses:
            # Check if the response exists
            cached_response = self.prompt_manager.retrieve_response(prompt_id)

        # Check for cached response
        cached_response = self.prompt_manager.retrieve_response(prompt_id) if self.use_cached_responses else None

        if cached_response:
            self.logger.info(f"Using cached response {type(cached_response)} from model: {model}")
            if isinstance(cached_response, str) and 'gpt' in model:
                resps = [json.loads(cached_response)]
            elif isinstance(cached_response, str):
                resps = cached_response.split("\n")
            elif isinstance(cached_response, list):
                resps = cached_response
            else:
                resps = cached_response
        else:
            # Make the request using the unified LLM client
            self.logger.info(
                f"Requesting datasets from content using model: {model}, temperature: {temperature}, "
                f"messages length: {self.count_tokens(messages, model)} tokens, schema: {response_format}")
            
            # Use the generic make_llm_call method
            raw_response = self.llm_client.make_llm_call(
                messages=messages, 
                temperature=temperature, 
                response_format=response_format,
                full_document_read=self.full_document_read
            )
            
            # Use the unified response processing method
            self.logger.debug(f"Calling process_llm_response with raw_response type: {type(raw_response)}")
            resps = self.llm_client.process_llm_response(
                raw_response=raw_response,
                response_format=response_format,
                expected_key="datasets"
            )
            self.logger.debug(f"process_llm_response returned: {resps} (type: {type(resps)})")
            
            # Apply task-specific deduplication
            self.logger.debug(f"Applying normalize_response_type to: {resps}")
            resps = self.normalize_response_type(resps)
            self.logger.debug(f"normalize_response_type returned: {resps} (type: {type(resps)})")
            
            # Save the processed response to cache
            if self.save_responses_to_cache:
                self.logger.debug(f"Saving response to cache with prompt_id: {prompt_id}")
                self.prompt_manager.save_response(prompt_id, resps)

        # Process the response content using extracted method
        result = self.process_datasets_response(resps)

        return result

    def process_datasets_response(self, resps):
        """
        Process the LLM response containing datasets and extract structured dataset information.
        This method handles different response formats (lists, strings, dicts) and performs validation.
        
        :param resps: LLM response containing datasets (can be list, string, or dict)
        :return: List of processed dataset dictionaries
        """
        # Process the response content
        result = []
        for dataset in resps:
            self.logger.info(f"Processing dataset: {dataset}")
            
            # Initialize variables to avoid UnboundLocalError
            dataset_id = None
            data_repository = None
            dataset_webpage = None
            
            # Handle malformed responses that create nested lists or unexpected structures
            if isinstance(dataset, list):
                self.logger.warning(f"Dataset is a list - likely malformed LLM response. Attempting to extract valid dictionaries...")
                # Try to extract valid dictionary items from the list
                valid_datasets = []
                for item in dataset:
                    if isinstance(item, dict) and any(key in item for key in ['dataset_identifier', 'dataset_id', 'data_repository']):
                        valid_datasets.append(item)
                        self.logger.info(f"Found valid dataset in list: {item}")
                
                # Process each valid dataset found in the list
                for valid_dataset in valid_datasets:
                    try:
                        dataset_id, data_repository, dataset_webpage = self.schema_validation(valid_dataset)
                        if dataset_id and data_repository:
                            dataset_result = {
                                "dataset_identifier": dataset_id,
                                "data_repository": data_repository,
                                "dataset_webpage": dataset_webpage if dataset_webpage is not None else 'n/a',
                                "citation_type": valid_dataset.get('citation_type', 'n/a')
                            }
                            # Preserve dataset_context_from_paper field if present (for PaperMiner enhanced schema)
                            if 'dataset_context_from_paper' in valid_dataset:
                                dataset_result['dataset_context_from_paper'] = valid_dataset['dataset_context_from_paper']
                            result.append(dataset_result)
                            self.logger.info(f"Successfully processed dataset from list: {result[-1]}")
                    except Exception as e:
                        self.logger.warning(f"Failed to process dataset from list: {e}")
                continue
            
            if type(dataset) == str:
                self.logger.info(f"Dataset is a string")
                # Skip short or invalid responses
                if len(dataset) < 3 or dataset.split(",")[0].strip() == 'n/a' and dataset.split(",")[
                    1].strip() == 'n/a':
                    continue
                if len(dataset.split(",")) < 2:
                    continue
                if re.match(r'\*\s+\*\*[\s\w]+:\*\*', dataset):
                    dataset = re.sub(r'\*\s+\*\*[\s\w]+:\*\*', '', dataset)

                dataset_id, data_repository = [x.strip() for x in dataset.split(",")[:2]]

            elif type(dataset) == dict:
                self.logger.info(f"Dataset is a dictionary")

                dataset_id, data_repository, dataset_webpage = self.schema_validation(dataset)
                
            else:
                self.logger.warning(f"Dataset is unexpected type {type(dataset)}, skipping: {dataset}")
                continue

            if (dataset_id is None or data_repository is None) and dataset_webpage is None:
                self.logger.info(f"Skipping dataset due to missing ID, repository, dataset page: {dataset}")
                continue

            if (dataset_id == 'n/a' or data_repository =='n/a') and dataset_webpage == 'n/a':
                self.logger.info(f"Skipping dataset due to missing ID, repository, dataset page: {dataset}")
                continue

            result.append({
                "dataset_identifier": dataset_id,
                "data_repository": data_repository,
                "dataset_webpage": dataset_webpage if dataset_webpage is not None else 'n/a',
                "citation_type": dataset.get('citation_type', 'n/a')
            })

            if 'decision_rationale' in dataset:
                result[-1]['decision_rationale'] = dataset['decision_rationale']

            if 'dataset-publication_relationship' in dataset:
                result[-1]['dataset-publication_relationship'] = dataset['dataset-publication_relationship']

            # Preserve dataset_context_from_paper field if present (for PaperMiner enhanced schema)
            if 'dataset_context_from_paper' in dataset:
                result[-1]['dataset_context_from_paper'] = dataset['dataset_context_from_paper']

            self.logger.info(f"Extracted dataset: {result[-1]}")

        self.logger.debug(f"Final result: {result}")
        return result

    def schema_validation(self, dataset, req_timeout=0.5):
        """
        Validate and extract dataset information based on the schema.

        :param dataset: dict — dataset information to be validated.

        :return: tuple — (dataset_id, data_repository, dataset_webpage) or (None, None, None) if invalid.
        """
        self.logger.info(f"Schema validation called with dataset: {dataset}")
        dataset_id, data_repository, dataset_webpage = None, None, None

        for repo_key, repo_vals in self.open_data_repos_ontology['repos'].items():
            for key, val in dataset.items():
                if 'dataset_webpage_url_ptr' in repo_vals:
                    ptr_search = re.sub('__ID__', '', repo_vals['dataset_webpage_url_ptr'])
                    if re.search(ptr_search, val, re.IGNORECASE):
                        self.logger.info(f"Matched dataset_webpage_url_ptr: {repo_vals['dataset_webpage_url_ptr']} to value: {val}")
                        if dataset_webpage is None:
                            self.logger.info(f"Candidate dataset_webpage: {val}")
                            dataset_webpage = val
                        if data_repository is None:
                            self.logger.info(f"Candidate data_repository: {repo_key}")
                            data_repository = self.resolve_data_repository(dataset.get('data_repository',
                                                                        dataset.get('repository_reference', 'n/a')),
                                                           identifier=dataset.get('dataset_identifier', dataset.get('dataset_id', 'n/a')),
                                                           dataset_page=dataset_webpage,
                                                           candidate_repo=repo_key)
                                                           
                if 'id_pattern' in repo_vals:
                    if re.search(repo_vals['id_pattern'], val, re.IGNORECASE):
                        self.logger.info(f"Matched id_pattern: {repo_vals['id_pattern']} to value: {val}")
                        if val.startswith('http'):
                            if dataset_webpage is None:
                                self.logger.info(f"Setting dataset_webpage to value: {val}")
                                dataset_webpage = val
                            ptr_sub = f'\b({repo_vals["id_pattern"]})'
                            self.logger.info(f"Using id_pattern to extract ID: {ptr_sub}")
                            match = re.search(ptr_sub, val, re.IGNORECASE)
                            if match and dataset_id is None:
                                self.logger.info(f"Setting dataset_id to value: {match.group(1)}")
                                dataset_id = match.group(1)
                            self.logger.info(f"Extracted ID: {dataset_id}")
                        else:
                            if (val.startswith('10.') or val.startswith('doi:10.')) and dataset_webpage is None:
                                self.logger.info(f"Setting dataset_webpage to DOI URL value: https://doi.org/{val}")
                                dataset_webpage = f"https://doi.org/{val}"
                                dataset_id = val
                            if dataset_id is None:
                                self.logger.info(f"Setting dataset_id to value: {val}")
                                dataset_id = val
                            if data_repository is None:
                                self.logger.info(f"Candidate data_repository: {repo_key}")
                                data_repository = self.resolve_data_repository(dataset.get('data_repository',
                                                                        dataset.get('repository_reference', 'n/a')),
                                                           identifier=dataset.get('dataset_identifier', dataset.get('dataset_id', 'n/a')),
                                                           dataset_page=dataset_webpage,
                                                           candidate_repo=repo_key)

        self.logger.info(f"Schema validation vals: {dataset_id}, {data_repository}, {dataset_webpage}")

        if dataset_id is None:
            dataset_id = self.validate_dataset_id(dataset.get('dataset_identifier', dataset.get('dataset_id', 'n/a')))
        else:
            self.logger.info(f"Dataset ID found via pattern matching: {dataset_id}")

        if data_repository is None:
            data_repository = self.resolve_data_repository(dataset.get('data_repository',
                                                                        dataset.get('repository_reference', 'n/a')),
                                                           identifier=dataset_id,
                                                           dataset_page=dataset_webpage)
        else:
            self.logger.info(f"Data repository found via pattern matching: {data_repository}")

        if dataset_webpage is None and 'dataset_webpage' in dataset:
            dataset_webpage = self.validate_dataset_webpage(dataset['dataset_webpage'], data_repository,
                                                            dataset_id, dataset, req_timeout=req_timeout)
        elif dataset_webpage is None:
            self.logger.info(f"Dataset webpage not extracted")
        else:
            self.logger.info(f"Dataset webpage found via pattern matching: {dataset_webpage}")
            dataset_webpage = self.validate_dataset_webpage(dataset_webpage, data_repository,
                                                            dataset_id, dataset, req_timeout=req_timeout)
        self.logger.info(f"Final schema validation vals: {dataset_id}, {data_repository}, {dataset_webpage}")

        if dataset_id == 'n/a' and data_repository in self.open_data_repos_ontology['repos']:
            self.logger.info(f"Dataset ID is 'n/a' and repository name from prompt")
            return None, None, None

        elif data_repository == 'n/a' and dataset_webpage == 'n/a':
            self.logger.info(f"Data repository is 'n/a', skipping dataset")
            return None, None, None

        return dataset_id, data_repository, dataset_webpage

    def normalize_response_type(self, response):
        """
        This function handles basic **postprocessing** of the LLM output.
        Normalize and deduplicate dataset responses by stripping DOI-style prefixes
        like '10.x/' from dataset IDs and keeping only one entry per PXD.

        :param response: List of dataset responses to be deduplicated (LLM Output).

        :return: List of deduplicated dataset responses.

        """
        self.logger.debug(f"normalize_response_type called with response type: {type(response)}, length: {len(response) if hasattr(response, '__len__') else 'N/A'}")
        self.logger.debug(f"normalize_response_type input: {response}")
        
        self.logger.info(f"Deduplicating response with {len(response)} items")
        seen = set()
        deduped = []

        if not isinstance(response, list) and isinstance(response, dict):
            self.logger.debug(f"Converting single dict to list")
            response = [response]
        elif not isinstance(response, list):
            self.logger.debug(f"Response is not a list or dict, type: {type(response)}")
            return response

        for i, item in enumerate(response):
            self.logger.debug(f"Processing item {i}: {item} (type: {type(item)})")
            self.logger.debug(f"Processing item: {item}")
            
            if isinstance(item, str):
                self.logger.debug(f"Item is a string, skipping deduplication logic")
                deduped.append(item)
                continue
                
            if not isinstance(item, dict):
                self.logger.debug(f"Item is not a dict, type: {type(item)}, appending as-is")
                deduped.append(item)
                continue
            
            dataset_id = item.get("dataset_identifier", item.get("dataset_id", ""))
            self.logger.debug(f"Extracted dataset_id: {dataset_id}")
            if not dataset_id:
                self.logger.debug(f"Skipping item with missing dataset_id: {item}")
                self.logger.warning(f"Skipping item with missing dataset_id: {item}")
                continue
            repo = item.get("data_repository", item.get("repository_reference", "n/a"))
            self.logger.debug(f"Extracted repo: {repo}")

            # Normalize: remove DOI prefix if it matches '10.x/PXD123456'
            clean_id = re.sub(r'10\.\d+/(\bPXD\d+\b)', r'\1', dataset_id)
            self.logger.debug(f"Normalized clean_id: {clean_id}")

            if clean_id not in seen:
                # Update the dataset_id to the normalized version
                item["dataset_id"] = clean_id
                self.logger.debug(f"Adding unique item: {clean_id}")
                self.logger.info(f"Adding unique item: {clean_id}")
                deduped.append(item)
                seen.add(clean_id)

            elif clean_id == 'n/a' and repo != 'n/a':
                self.logger.debug(f"Adding n/a dataset_id with valid repo: {repo}")
                deduped.append(item)

            else:
                self.logger.debug(f"Duplicate found and skipped: {clean_id}")
                self.logger.info(f"Duplicate found and skipped: {clean_id}")

        self.logger.debug(f"normalize_response_type final result: {deduped}")
        return deduped

    def safe_parse_json(self, response_text):
        """
        Wrapper method for backward compatibility.
        Delegates to the LLMClient's safe_parse_json method.
        """
        self.logger.debug(f"Parser safe_parse_json wrapper called, delegating to client")
        return self.llm_client.safe_parse_json(response_text)

    def process_data_availability_links(self, dataset_links):
        """
        Given the link, the article title, and the text around the link, create a column (identifier),
        and a column for the dataset.

        :param dataset_links: List of dictionaries containing href links and their context.

        :return: List of dictionaries containing processed dataset information.

        """
        self.logger.info(f"Analyzing data availability statement with {len(dataset_links)} links")
        self.logger.debug(f"Text from data-availability: {dataset_links}")

        model = self.llm_name
        temperature = 0.0

        ret = []
        progress = 0

        for link in dataset_links:
            self.logger.info(f"Processing link: {link['href']}")

            if progress > len(dataset_links):
                break

            ret_element = {}

            # Detect if the link is already a dataset webpage
            detected = self.dataset_webpage_url_check(link['href'])
            if detected is not None:
                self.logger.info(f"Link {link['href']} points to dataset webpage")
                ret.append(detected)
                progress += 1
                continue

            # Prepare the dynamic prompt
            dynamic_content = {
                "href": link['href'],
                "surrounding_text": link['surrounding_text']
            }
            static_prompt = self.prompt_manager.load_prompt("GEMINI_RTR_FewShot")
            messages = self.prompt_manager.render_prompt(static_prompt, self.full_document_read, **dynamic_content)

            # Generate a unique checksum for the prompt
            prompt_id = f"{model}-{temperature}-{self.prompt_manager._calculate_checksum(str(messages))}"
            self.logger.info(f"Prompt ID: {prompt_id}")

            # Check if the response exists
            cached_response = self.prompt_manager.retrieve_response(prompt_id) if self.use_cached_responses else None
            if cached_response:
                self.logger.info("Using cached response.")
                resp = cached_response.split("\n") if isinstance(cached_response, str) else cached_response
            else:
                # Make the request using the unified LLM client
                self.logger.info(f"Requesting datasets using model: {model}, messages: {messages}")
                
                # Use the generic make_llm_call method
                raw_response = self.llm_client.make_llm_call(
                    messages=messages, 
                    temperature=0.0, 
                    full_document_read=False
                )
                
                # Process response and save to cache
                resp = raw_response.split("\n") if isinstance(raw_response, str) else [raw_response]
                if self.save_responses_to_cache:
                    self.prompt_manager.save_response(prompt_id, raw_response)
                self.logger.info(f"Response saved to cache")

            # Process the response
            ret_element['link'] = link['href']
            ret_element['content_type'] = 'data_link'

            if type(resp) == list:
                for r in resp:
                    append_item = ret_element.copy()
                    self.logger.info(f"Response: '{r}', len: {len(r)}")
                    # string that is less than 1 char + 1 comma + 1 char
                    if len(r) < 3:
                        continue
                    # skip strings that do not conform to expected output
                    if r.count(',') != 1:
                        continue
                    append_item['dataset_identifier'], append_item['data_repository'] = r.split(
                        ',')
                    append_item['dataset_identifier'] = append_item['dataset_identifier'].strip()
                    append_item['data_repository'] = append_item['data_repository'].strip()
                    append_item['source_section'] = link['source_section']
                    append_item['retrieval_pattern'] = link[
                        'retrieval_pattern'] if 'retrieval_pattern' in link.keys() else None
                    ret.append(append_item)
                    self.logger.info(f"Response appended to df {append_item}")
                    progress += 1
                self.logger.info(f"Updated ret: {ret}")
            else:
                self.logger.info(f"Response: '{resp}', len: {len(resp)}. Response appended to df")
                ret_element['dataset_identifier'], ret_element['data_repository'] = (
                    response['message']['content'].split(','))
                # trim leading and trailing whitespaces
                ret_element['dataset_identifier'] = ret_element['dataset_identifier'].strip()
                ret_element['data_repository'] = ret_element['data_repository'].strip()
                ret_element['source_section'] = link['source_section']
                ret_element['retrieval_pattern'] = link[
                    'retrieval_pattern'] if 'retrieval_pattern' in link.keys() else None
                ret.append(ret_element)
                progress += 1

        return ret

    def brute_force_dataset_webpage_url_check(self, url):
        """
        Iterate over all the known data repositories and check if the URL matches any of their dataset webpage patterns.
        """
        result = None
        self.logger.info(f"Brute-force checking if link points to dataset webpage: {url}")
        for repo in self.open_data_repos_ontology['repos'].keys():
            if 'dataset_webpage_url_ptr' in self.open_data_repos_ontology['repos'][repo]:
                pattern = self.open_data_repos_ontology['repos'][repo]['dataset_webpage_url_ptr']
                result = re.search(pattern, url, re.IGNORECASE)
            if result is not None:
                self.logger.info(f"Link {url} points to dataset webpage in repo {repo}")
                return url
        return None

    def dataset_webpage_url_check(self, url, resolved_repo=None):
        """
        Check if the URL directly points to a dataset webpage.

        :param url: str — the URL to be checked.

        :return: dict or None — dictionary with data repository information if one pattern from ontology matches that
        """
        ret = {}
        self.logger.info(f"Checking if link points to dataset webpage: {url}")
        repo = self.resolve_data_repository(url) if resolved_repo is None else resolved_repo
        self.logger.info(f"Extracted domain: {repo}")
        if (repo in self.open_data_repos_ontology['repos'].keys() and
                'dataset_webpage_url_ptr' in self.open_data_repos_ontology['repos'][repo].keys()):
            self.logger.info(f"Link {url} could point to dataset webpage")
            pattern = self.open_data_repos_ontology['repos'][repo]['dataset_webpage_url_ptr']
            self.logger.debug(f"Pattern: {pattern}")
            match = re.match(pattern, url)
            # if the link matches the pattern, extract the dataset identifier and the data repository
            if match:
                self.logger.info(f"Match with pattern: {pattern}")
                ret['data_repository'] = repo
                ret['dataset_identifier'] = match.group(1)
                ret['dataset_webpage'] = url
                ret['link'] = url
                return ret
            elif re.search(re.sub(pattern, '__ID__', '', re.IGNORECASE), url):
                self.logger.info(f"Link matches the pattern {pattern} with __ID__ replaced")
                extracted_id = 'n/a'
                ret['data_repository'] = repo
                if 'id_pattern' in self.open_data_repos_ontology['repos'][repo].keys():
                    ptr_sub = f'.*({self.open_data_repos_ontology["repos"][repo]["id_pattern"]}).*'
                    self.logger.info(f"Using id_pattern to extract ID: {ptr_sub}")
                    match = re.search(ptr_sub, url, re.IGNORECASE)
                    if match:
                        extracted_id = match.group(1)
                    self.logger.info(f"Extracted ID: {extracted_id}")
                ret['dataset_identifier'] = extracted_id
                ret['dataset_webpage'] = url
                ret['link'] = url
                return ret
            else:
                self.logger.info(f"Link does not match the pattern")
                return None

        return None

    def normalize_LLM_output(self, response):
        cont = response['message']['content']
        self.logger.info(f"Normalizing {type(cont)} LLM output: {cont}")
        output = cont.split(",")
        repo = re.sub(r"[\n\s]*", "", output.pop())
        self.logger.info(f"Repo: {repo}")
        ret = []
        for i in range(len(output)):
            ret.append(re.sub(r"\s*and\s+", " ", output[i]) + "," + repo)
        return ret

    def url_to_repo_domain(self, url, dataset_webpage_url=None):

        self.logger.info(f"Function call: url_to_repo_domain({url},{dataset_webpage_url})")

        if dataset_webpage_url is not None:
            url = dataset_webpage_url

        if url in self.open_data_repos_ontology['repos'].keys():
            return url

        self.logger.info(f"Extracting repo domain from URL: {url}")
        match = re.match(r'^https?://([\.\w\-]+)\/*', url)
        if match:
            domain = match.group(1)
            self.logger.debug(f"Repo Domain: {domain}")
            if (domain in self.open_data_repos_ontology['repos'].keys() and
                    'repo_mapping' in self.open_data_repos_ontology['repos'][domain].keys()):
                return self.open_data_repos_ontology['repos'][domain]['repo_mapping']
            return domain
        elif '.' not in url:
            return url
        elif ' ' not in url and '/' not in url:
            self.logger.warning(f"URL {url} may be a domain already.")
            return url
        else:
            self.logger.error(f"Error extracting domain from URL: {url}")
            return 'Unknown_Publisher'

    def get_all_repo_names(self, uncased=False):
        # Get the all the repository names from the config file. (all the repos in ontology)
        repo_names = []
        for k, v in self.open_data_repos_ontology['repos'].items():
            if 'repo_name' in v.keys():
                repo_names.append(v['repo_name'])
            else:
                repo_names.append(k)
        repo_names = [x.lower() for x in repo_names] if uncased else repo_names
        self.logger.debug(f"All repository names: {repo_names}")
        return repo_names

    def get_repo_domain_to_name_mapping(self):
        # Get the mapping of repository domains to names from ontology
        repo_mapping = {}
        for k, v in self.open_data_repos_ontology['repos'].items():
            if 'repo_name' in v.keys():
                repo_mapping[k] = v['repo_name'].lower()
            else:
                repo_mapping[k] = k

        ret = {v: k for k, v in repo_mapping.items()}
        self.logger.debug(f"Repo mapping: {ret}")
        return ret

    def validate_dataset_id(self, dataset_identifier):
        """
        This function checks for hallucinations, i.e. if the dataset identifier is a known repository name.
        """
        self.logger.info(f"Validating accession ID: {dataset_identifier}")
        if dataset_identifier.lower() in self.get_all_repo_names(uncased=True):
            self.logger.info(f"Accession ID {dataset_identifier} is a known repository --> invalid, returning 'n/a'")
            return 'n/a'
        elif ' ' in dataset_identifier or dataset_identifier == 'n/a' or len(dataset_identifier) < 3:
            self.logger.info(f"Accession ID {dataset_identifier} is invalid")
            return 'n/a'
        elif dataset_identifier.startswith('http') and 'doi.org' in dataset_identifier:
            dataset_identifier = re.sub(r'https?://doi\.org/', '', dataset_identifier, re.IGNORECASE)
            dataset_identifier = re.sub(r'doi:', '', dataset_identifier, re.IGNORECASE)
            return dataset_identifier
        elif dataset_identifier.startswith('http'):
            new_metadata = self.dataset_webpage_url_check(dataset_identifier)
            new_id = new_metadata['dataset_identifier'] if new_metadata is not None else 'n/a'
            self.logger.info(f"Accession ID {new_id} is valid") if new_id != 'n/a' else self.logger.info(
                f"Accession ID {dataset_identifier} is invalid")
            return new_id
        else:
            self.logger.info(f"Accession ID {dataset_identifier} is valid")
            return dataset_identifier

    def validate_dataset_webpage(self, dataset_webpage_url, resolved_repo, dataset_id, old_metadata=None, req_timeout=0.5):
        """
        This function checks for hallucinations, i.e. if the dataset identifier is a known repository name.
        Input:
        dataset_webpage_url: str - the URL to be validated
        resolved_repo: str - the resolved repository name
        dataset_id: str - the dataset identifier
        old_metadata: dict - the old metadata dictionary (optional)
        """
        self.logger.info(f"Validating Dataset Page: {dataset_webpage_url}, resolved_repo {resolved_repo}, dataset_id {dataset_id}")
        resolved_dataset_page = self.resolve_url(dataset_webpage_url, req_timeout=req_timeout)

        if resolved_repo in self.open_data_repos_ontology['repos']:
            if 'dataset_webpage_url_ptr' in self.open_data_repos_ontology['repos'][resolved_repo].keys():
                dataset_webpage_url_ptr = self.open_data_repos_ontology['repos'][resolved_repo]['dataset_webpage_url_ptr']
                pattern = re.sub(r'__ID__', '', dataset_webpage_url_ptr)
                self.logger.info(f"Pattern: {pattern}, resolved_dataset_page: {resolved_dataset_page}")
                if re.search(pattern, resolved_dataset_page, re.IGNORECASE) or pattern in resolved_dataset_page:
                    self.logger.info(f"Link matches the pattern {pattern} of resolved_dataset_page.")
                    return resolved_dataset_page
                else:
                    self.logger.warning(f"Link does not match expected pattern {pattern} but may still be valid after redirect.")
                    # Check if the resolved URL contains the dataset_id as a fallback
                    if dataset_id and dataset_id != 'n/a' and dataset_id in resolved_dataset_page:
                        self.logger.info(f"Dataset ID {dataset_id} found in resolved URL, accepting as valid.")
                        return resolved_dataset_page
                    # Try brute-force checking if it matches any known repository patterns
                    brute_force_result = self.brute_force_dataset_webpage_url_check(resolved_dataset_page)
                    if brute_force_result is not None:
                        self.logger.info(f"Brute-force validation found valid dataset webpage: {brute_force_result}")
                        return resolved_dataset_page
                    # As a last resort, return the resolved URL instead of 'n/a' to preserve information
                    self.logger.warning(f"Pattern validation failed but returning resolved URL to preserve potential valid link.")
                    return resolved_dataset_page
            else:
                self.logger.info(f"No dataset_webpage_url_ptr found for {resolved_repo}")
                return resolved_dataset_page
        elif dataset_id in resolved_dataset_page:
            self.logger.info(f"Dataset ID {dataset_id} found in resolved dataset page {resolved_dataset_page}")
            return resolved_dataset_page
        elif old_metadata is not None:
            for k,v in old_metadata.items():
                self.logger.info(f"Brute-force checking old metadata {k}: {v}")
                checked_url = self.brute_force_dataset_webpage_url_check(v)
                if checked_url is not None:
                    self.logger.info(f"Found valid dataset webpage in old metadata {k}: {checked_url}")
                    return checked_url

        # Final fallback: if repository is not in ontology but URL seems valid, preserve it
        if resolved_repo not in self.open_data_repos_ontology['repos']:
            self.logger.warning(f"Repository {resolved_repo} not found in ontology, but preserving resolved URL.")
            # Check if the resolved URL looks like a valid dataset page (contains common patterns)
            if any(indicator in resolved_dataset_page.lower() for indicator in ['dataset', 'data', 'accession', 'id=']):
                self.logger.info(f"Resolved URL appears to contain dataset-related content, preserving it.")
                return resolved_dataset_page
            
        self.logger.warning(f"All validation methods failed, returning original URL to preserve information.")
        return resolved_dataset_page

    def resolve_url(self, url, req_timeout=0.5):
        if req_timeout is None:
            return url
        try:
            response = requests.get(url, allow_redirects=True, timeout=req_timeout)
            self.logger.info(f"Resolved URL: {response.url}")
            return response.url
        except requests.RequestException as e:
            self.logger.warning(f"Error resolving URL {url}: {e}")
            return url

    def resolve_accession_id_for_repository(self, dataset_identifier, data_repository, resolved_dataset_page=None):
        """
        This function resolves the accession ID for a given dataset identifier and data repository.
        It checks if the dataset identifier matches the expected pattern for the given repository (from ontology)
        """
        self.logger.info(f"Resolving accession ID for {dataset_identifier} in {data_repository}, resolved page: {resolved_dataset_page}")
        if data_repository in self.open_data_repos_ontology['repos']:
            repo_config = self.open_data_repos_ontology['repos'][data_repository]
            pattern = repo_config.get('id_pattern')
            if pattern and not re.match(pattern, dataset_identifier, re.IGNORECASE):
                self.logger.warning(f"Identifier {dataset_identifier} does not match pattern for {data_repository}")
            else:
                self.logger.warning(f"id_pattern not defined for {data_repository} in ontology. Add definition to improve validation.")

            if pattern and resolved_dataset_page is not None:
                self.logger.info(f"Extracting ID from dataset page {resolved_dataset_page} using pattern {pattern}")
                match = re.search(f"({pattern})", resolved_dataset_page, re.IGNORECASE)
                if match:
                    dataset_identifier = match.group(1)
                    self.logger.info(f"Extracted ID: {dataset_identifier}")

            if 'default_id_suffix' in repo_config and not dataset_identifier.endswith(repo_config['default_id_suffix']):
                return dataset_identifier.lower() + repo_config['default_id_suffix']

        else:
            self.logger.warning(f"Repository {data_repository} not found in ontology")
    
        return dataset_identifier

    def resolve_data_repository(self, repo: str, identifier=None, dataset_page=None, candidate_repo=None) -> str:
        """
        Normalize the repository domain from a URL or text reference using config mappings in ontology.

        :param repo: str — the repository name or URL to be normalized.

        :return: str — the normalized repository name.
        """
        self.logger.info(f"Resolving data repository for candidate: {repo}, identifier: {identifier}, dataset_page: {dataset_page}")

        if repo is None:
            self.logger.warning(f"Repository is None")
            return 'n/a'

        if ',' in repo and ',' in identifier:
            self.logger.warning(f"Repository contains a comma: {repo}. Same data may be in multiple repos.")
            ret = []
            for r in repo.split(','):
                r = r.strip()
                if r in self.open_data_repos_ontology['repos']:
                    ret.append(self.resolve_data_repository(r).lower())
            return ret

        if isinstance(repo, list):
            self.logger.warning(f"Repository is a list: {repo}. Same data may be in multiple repos.")
            ret = []
            for r in repo:
                r = r.strip()
                if r in self.open_data_repos_ontology['repos']:
                    ret.append(self.resolve_data_repository(r).lower())
            return ret

        if repo.startswith('http'):
            check_url = self.brute_force_dataset_webpage_url_check(repo)
            if check_url:
                self.logger.info(f"Repository {repo} is a dataset webpage {check_url}")
                return check_url

        resolved_to_known_repo = False

        for k, v in self.open_data_repos_ontology['repos'].items():
            self.logger.debug(f"Checking if {repo} == {k}. Repo vals: {v.keys()}")
            repo = re.sub(r"\(", " ", repo)
            repo = re.sub(r"\)", " ", repo)
            # match where repo_link has been extracted
            if k.lower() == repo.lower():
                self.logger.info(f"Exact - case insensitive - match found for repo: {repo}")
                resolved_to_known_repo = True
                repo = k
                break

            if not resolved_to_known_repo and 'repo_name' in v.keys():
                if repo.lower() == v['repo_name'].lower():
                    self.logger.info(f"Found repo_name match for {repo}")
                    repo = k
                    resolved_to_known_repo = True
                    break

                elif v['repo_name'].lower() in repo.lower():
                    self.logger.info(f"Found partial match for {repo} in {v['repo_name']}")
                    repo = k
                    resolved_to_known_repo = True
                    break

            if not resolved_to_known_repo and identifier is not None and identifier != 'n/a' and 'id_pattern' in v.keys():
                self.logger.debug(f"Checking id_pattern {v['id_pattern']} match with identifier {identifier} for {repo}")
                if re.match(v['id_pattern'], identifier, re.IGNORECASE):
                    self.logger.info(f"Found id_pattern match for {repo} in {v['id_pattern']}")
                    repo = k
                    resolved_to_known_repo = True
                    break

        if not resolved_to_known_repo:
            repo = self.url_to_repo_domain(repo, dataset_page)
            self.logger.info(f"data_repository not resolved, using domain")

        if repo in self.open_data_repos_ontology['repos'] and 'repo_mapping' in self.open_data_repos_ontology['repos'][
            repo]:
            repo = self.open_data_repos_ontology['repos'][repo]['repo_mapping']
            self.logger.info(f"Resolved data repository: {repo}")
        
        if candidate_repo is not None and candidate_repo in self.open_data_repos_ontology['repos'] and \
            'repo_root' in self.open_data_repos_ontology['repos'][candidate_repo] and \
            self.open_data_repos_ontology['repos'][candidate_repo]['repo_root'] == repo:
            self.logger.info(f"Using candidate repo {candidate_repo} as it matches the resolved repo config.")
            return candidate_repo.lower()

        return repo.lower()  # fallback

    def get_dataset_page(self, datasets):
        """
        Enhance dataset dictionaries with missing dataset webpage URLs and access modes.
        This function only acts on datasets that don't already have valid webpage URLs,
        preserving existing good data from schema validation.

        :param datasets: list of dictionaries containing dataset information.
        :return: list of dictionaries with updated dataset information including dataset webpage URL.
        """
        if datasets is None:
            return None

        self.logger.info(f"Enhancing dataset pages for {len(datasets)} datasets")

        for i, item in enumerate(datasets):
            if type(item) != dict:
                self.logger.error(f"Can't process non-dict item {1 + i}: {item}")
                continue

            # Skip if we already have a valid dataset webpage (preserve schema validation results)
            existing_webpage = item.get('dataset_webpage', item.get('dataset_page', None))
            if existing_webpage and existing_webpage != 'n/a' and existing_webpage != 'na':
                self.logger.debug(f"Dataset {1 + i} already has valid webpage: {existing_webpage}")
                # Still add access_mode if missing
                self._add_access_mode_if_missing(item, i)
                continue

            self.logger.info(f"Processing dataset {1 + i} - missing or invalid webpage")

            # Get required fields
            repo = item.get('data_repository', item.get('repository_reference', None))
            accession_id = item.get('dataset_identifier', item.get('dataset_id', 'n/a'))
            
            if repo is None or repo == 'n/a' or accession_id == 'n/a':
                self.logger.info(f"Skipping dataset {1 + i}: missing repo ({repo}) or accession_id ({accession_id})")
                continue

            # Handle list repositories (shouldn't happen after schema validation, but be defensive)
            if isinstance(repo, list):
                if len(repo) > 0:
                    self.logger.warning(f"Repository is a list: {repo}. Using first element.")
                    repo = repo[0]
                else:
                    self.logger.warning("Repository list is empty. Skipping dataset.")
                    continue

            # Resolve accession ID if needed
            resolved_accession_id = self.resolve_accession_id_for_repository(accession_id, repo, existing_webpage)

            # Try to construct dataset webpage URL
            dataset_webpage = self._construct_dataset_webpage(repo, resolved_accession_id, existing_webpage)
            
            if dataset_webpage and dataset_webpage != 'n/a':
                datasets[i]['dataset_webpage'] = dataset_webpage
                self.logger.info(f"Added dataset webpage for {1 + i}: {dataset_webpage}")
            else:
                self.logger.warning(f"Could not construct valid webpage for dataset {1 + i}")
                datasets[i]['dataset_webpage'] = 'n/a'

            # Add access mode
            self._add_access_mode_if_missing(item, i)

        self.logger.info(f"Dataset enhancement completed: {len(datasets)} datasets processed")
        return datasets

    def _construct_dataset_webpage(self, repo, accession_id, existing_webpage):
        """Helper method to construct dataset webpage URL using ontology patterns."""
        if repo in self.open_data_repos_ontology['repos']:
            repo_config = self.open_data_repos_ontology['repos'][repo]
            
            if "dataset_webpage_url_ptr" in repo_config:
                dataset_page_ptr = repo_config['dataset_webpage_url_ptr']
                
                # Check if existing webpage already matches the pattern
                if existing_webpage:
                    pattern_base = dataset_page_ptr.replace('__ID__', '')
                    if re.search(re.escape(pattern_base), existing_webpage, re.IGNORECASE):
                        self.logger.debug(f"Existing webpage {existing_webpage} matches pattern")
                        return existing_webpage
                
                # Construct new URL using pattern
                constructed_url = re.sub('__ID__', accession_id, dataset_page_ptr)
                self.logger.info(f"Constructed webpage URL: {constructed_url}")
                return constructed_url
            else:
                self.logger.debug(f"No dataset_webpage_url_ptr found for repo: {repo}")
                return existing_webpage
        
        elif repo.startswith('http'):
            # Repository itself is a URL, use it as the dataset webpage
            self.logger.info(f"Using repo URL as dataset webpage: {repo}")
            return repo
        
        else:
            self.logger.warning(f"Repository {repo} not found in ontology")
            return None

    def _add_access_mode_if_missing(self, item, index):
        """Helper method to add access_mode if missing."""
        if 'access_mode' not in item:
            repo = item.get('data_repository', item.get('repository_reference', None))
            if repo and repo in self.open_data_repos_ontology['repos']:
                repo_config = self.open_data_repos_ontology['repos'][repo]
                if 'access_mode' in repo_config:
                    access_mode = repo_config['access_mode']
                    item['access_mode'] = access_mode
                    self.logger.info(f"Added access mode for dataset {index + 1}: {access_mode}")

    def get_NuExtract_template(self):
        """
        template = '''{
                    "Available Dataset": {
                        "data repository name" = "",
                        "data repository link" = "",
                        "dataset identifier": "",
                        "dataset webpage": "",
            }
            }'''

            return template
            """
        raise NotImplementedError("This method should be implemented in a subclass.")

    def tokens_over_limit(self, html_cont: str, model="gpt-4", limit=128000, allowance_static_prompt=200):
        # Use tiktoken only for OpenAI models, fallback to rough estimate for others
        if 'gpt-4' in model:
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(html_cont)
            self.logger.info(f"Number of tokens: {len(tokens)}")
            return len(tokens) + int(allowance_static_prompt * 1.25) > limit
        else:
            # Rough estimate: 1 token ≈ 4 characters
            n_tokens = len(html_cont) // 4
            self.logger.info(f"Estimated number of tokens for model '{model}': {n_tokens}")
            return n_tokens + int(allowance_static_prompt * 1.25) > limit

    def count_tokens(self, prompt, model="gpt-4o-mini") -> int:
        """
        Count the number of tokens in a given prompt for a specific model.

        :param prompt: str — the prompt to be tokenized.

        :param model: str — the model name (default: "gpt-4").

        :return: int — the number of tokens in the prompt.
        """
        n_tokens = 0

        # **Ensure `prompt` is a string**
        if isinstance(prompt, list):
            self.logger.info(f"Expected string but got list. Converting list to string.")
            prompt = " ".join([msg["content"] for msg in prompt if isinstance(msg, dict) and "content" in msg])

        elif not isinstance(prompt, str):
            self.logger.error(f"Unexpected type for prompt: {type(prompt)}. Converting to string.")
            prompt = str(prompt)

        self.logger.debug(f"Counting tokens for model: {model}, prompt length: {len(prompt)} char")
        # **Token count based on model**
        if 'gpt' in model:
            encoding = tiktoken.encoding_for_model(model)
            n_tokens = len(encoding.encode(prompt))

        elif 'gemini' in model or 'gemma' in model:
            try:
                n_tokens = len(prompt) // 4  # Adjust based on the response structure
                self.logger.debug(f"Rough estimate of token count for Gemini model '{model}': {n_tokens}")
            except Exception as e:
                self.logger.error(f"Error counting tokens for Gemini model '{model}': {e}")
                n_tokens = 0

        return n_tokens

    def parse_datasets_metadata(self, metadata: str, model='gemini-2.0-flash', use_portkey=True,
                                prompt_name='gpt_metadata_extract') -> dict:
        """
        Given the metadata, extract the dataset information using the LLM.

        :param metadata: str — the metadata to be parsed.

        :param model: str — the model to be used for parsing (default: 'gemini-2.0-flash').

        :return: dict — the extracted metadata. This is sometimes project metadata, or study metadata, or dataset metadata. Ontology enhancement is needed to distinguish between these.
        """
        #metadata = self.normalize_full_DOM(metadata)
        self.logger.info(f"Parsing metadata len: {len(metadata)}")
        dataset_info = self.extract_dataset_info(metadata, subdir='metadata_prompts',
                                                 use_portkey=use_portkey,
                                                 prompt_name=prompt_name)
        return dataset_info

    def flatten_metadata_dict(self, metadata: dict, parent_key: str = '', sep: str = '.') -> dict:
        """
        Recursively flattens a nested dictionary, concatenating keys with `sep`.
        Lists of dicts are expanded with their index.
        """
        items = []
        for k, v in metadata.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_metadata_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, dict):
                        items.extend(self.flatten_metadata_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, v))
        return dict(items)

    def extract_dataset_info(self, metadata, subdir='', model=None, use_portkey=True,
                             prompt_name='gpt_metadata_extract'):
        """
        Given the metadata, extract the dataset information using the LLM.

        :param model: str — the model to be used for parsing (default: self.llm_name).

        :param metadata: str — the metadata to be parsed.

        :param subdir: str — the subdirectory for the prompt template (default: '').

        :return: dict — the extracted metadata. This is sometimes project metadata, or study metadata, or dataset
         metadata
        """
        self.logger.info(f"Extracting dataset information from metadata. Prompt from subdir: {subdir}")

        llm = LLMClient_dev(
            model=model if model else self.llm_name,
            logger=self.logger,
            save_dynamic_prompts=self.save_dynamic_prompts,
            use_portkey=use_portkey
        )
        
        # Load and render the prompt using the unified client
        static_prompt = llm.prompt_manager.load_prompt("gpt_metadata_extract", subdir=subdir)
        messages = llm.prompt_manager.render_prompt(static_prompt, entire_doc=True, content=metadata)
        
        # Make the LLM call using the unified interface
        response = llm.make_llm_call(messages=messages, temperature=0.0)

        # Post-process response into structured dict
        dataset_info = self.safe_parse_json(response)
        self.logger.info(f"Extracted dataset info: {dataset_info}")
        return dataset_info

    def semantic_retrieve_from_corpus(self, corpus, model_name='sentence-transformers/all-MiniLM-L6-v2',
                                      topk_docs_to_retrieve=5, query=None):
        """
        Given a corpus of text, retrieve the most relevant documents using semantic search.

        :param corpus: list of str — the corpus of text to search.

        :param model_name: str — the name of the embedding model to use (default: 'sentence-transformers/all-MiniLM-L6-v2').

        :param topk_docs_to_retrieve: int — the number of top documents to retrieve (default: 5).

        :return: list of dict — the most relevant documents from the corpus.
        """

        if query is None:
            query = """Explicitly identify all the datasets by their database accession codes, repository names, and links
                    to deposited datasets mentioned in this paper."""

        retriever = EmbeddingsRetriever(
            corpus=corpus,
            model_name=model_name,  # or any other model you prefer
            device="cpu",
            logger=self.logger
        )
        # Other queries can be used here as well, e.g.:
        # "Available data, accession code, data repository, deposited data"
        # "Explicitly identify all database accession codes, repository names, and links to deposited datasets or ...
        # ...supplementary data mentioned in this paper."
        # "Deposited data will be available in the repository XYZ, with accession code ABC123."
        # """Data availability statement, dataset reference, digital repository name, dataset identifier,
        #         dataset accession code, dataset doi, dataset page"""

        result = retriever.search(
            query=query,
            k=topk_docs_to_retrieve
        )

        return result

    def regex_match_id_patterns(self, document, id_patterns=None):
        """
        Extract dataset identifiers from document using regex patterns from ontology.
        
        :param document: str - the document content to search for patterns
        :return: list - list of matches found using ontology patterns
        """
        self.logger.info(f"Extracting dataset IDs using regex patterns from document")
        matches = []

        if id_patterns is None:
            id_patterns = [repo_config['id_pattern'] for repo_name, repo_config in self.open_data_repos_ontology['repos'].items() if 'id_pattern' in repo_config]

        for pattern in id_patterns:
            self.logger.debug(f"Checking pattern {pattern} for document")
            found_matches = re.findall(pattern, document, re.IGNORECASE)
            if found_matches:
                self.logger.info(f"Found {len(found_matches)} matches for pattern {pattern}: {found_matches}")
                matches.extend(found_matches)

        self.logger.info(f"Total matches found: {len(matches)}")
        return matches

