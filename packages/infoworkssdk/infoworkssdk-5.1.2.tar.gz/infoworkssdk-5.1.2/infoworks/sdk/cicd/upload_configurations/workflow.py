import base64
import json
import traceback
import time

from infoworks.sdk.url_builder import list_sources_url, create_workflow_url, list_domains_url, configure_workflow_url,list_pipeline_versions_url,list_pipelines_url,list_users_url
from infoworks.sdk.utils import IWUtils
import sys
import configparser
import requests
from infoworks.sdk.cicd.upload_configurations.domains import Domain
from infoworks.core.iw_authentication import get_bearer_token
from infoworks.sdk.cicd.upload_configurations.utils import Utils
from infoworks.sdk.cicd.upload_configurations.update_configurations import InfoworksDynamicAccessNestedDict
from infoworks.sdk.cicd.upload_configurations.local_configurations import PRE_DEFINED_MAPPINGS

class Workflow:
    def __init__(self, workflow_configuration_path, replace_words=""):
        with open(workflow_configuration_path, 'r') as file:
            json_string = file.read()
            if replace_words != "":
                for key, value in [item.split("->") for item in replace_words.split(";")]:
                    json_string = json_string.replace(key, value)
        self.configuration_obj = IWUtils.ejson_deserialize(json_string)

    def update_mappings_for_configurations(self, mappings):
        config = configparser.ConfigParser()
        config.read_dict(mappings)
        d = InfoworksDynamicAccessNestedDict(self.configuration_obj)
        for section in config.sections():
            if section in PRE_DEFINED_MAPPINGS:
                continue
            try:
                final = d.setval(section.split("$"), dict(config.items(section)))
            except KeyError as e:
                pass
        self.configuration_obj = d.data
        iw_mappings = self.configuration_obj.get("configuration", {}).get("iw_mappings", [])
        try:
            if "domain_name_mappings" in config.sections():
                domain_mappings = dict(config.items("domain_name_mappings"))
                if domain_mappings!={}:
                    for mapping in iw_mappings:
                        domain_name = mapping.get("recommendation", {}).get("domain_name", "")
                        if domain_name != "" and domain_mappings != {}:
                            mapping["recommendation"]["domain_name"] = domain_mappings.get(domain_name.lower(), domain_name)
                    self.configuration_obj["configuration"]["iw_mappings"]=iw_mappings
        except Exception as e:
            print("Failed while doing the domain mappings")
            print(str(e))
            print(traceback.format_exc())
        # handle any other generic name mappings like iw_mappings$recommendation$source_name
        try:
            generic_mappings = [i for i in config.sections() if i.lower().startswith("iw_mappings$")]
            for mapping in generic_mappings:
                lineage_list = mapping.split("$")
                lineage_list.remove("iw_mappings")
                if "recommendation" in lineage_list:
                    lineage_list.remove("recommendation")
                artifact_type = lineage_list[0]
                artifact_mappings = dict(config.items(f"iw_mappings$recommendation${artifact_type}"))
                if artifact_mappings != {}:
                    for mapping in iw_mappings:
                        artifact_name = mapping.get("recommendation", {}).get(artifact_type, "")
                        if artifact_name != "" and artifact_mappings != {}:
                            mapping["recommendation"][artifact_type] = artifact_mappings.get(artifact_name.lower(),
                                                                                             artifact_name)
                    self.configuration_obj["configuration"]["iw_mappings"] = iw_mappings
        except Exception as e:
            print("Failed while doing the generic mappings")
            print(str(e))
            print(traceback.format_exc())

    def get_existing_domain_id(self,wf_client_obj,domain_name):
        existing_domain_id=None
        if domain_name is not None:
            domains_url_base = list_domains_url(wf_client_obj.client_config)
            filter_condition = IWUtils.ejson_serialize({"name": domain_name})
            domains_url = domains_url_base + f"?filter={{filter_condition}}".format(filter_condition=filter_condition)
            response = requests.request("GET", domains_url, headers={
                'Authorization': 'Bearer ' + wf_client_obj.client_config["bearer_token"],
                'Content-Type': 'application/json'}, verify=False)
            if response.status_code == 406:
                headers = wf_client_obj.regenerate_bearer_token_if_needed(
                    {'Authorization': 'Bearer ' + wf_client_obj.client_config["bearer_token"],
                     'Content-Type': 'application/json'})
                response = requests.request("GET", domains_url, headers=headers, verify=False)
            existing_domain_id = None
            if response is not None:
                result = response.json().get("result", [])
                if len(result) > 0:
                    existing_domain_id = result[0]["id"]
                else:
                    wf_client_obj.logger.error('Can not find domain with given name {} '.format(domain_name))
                    wf_client_obj.logger.error('Unable to create workflow')
                    print(f'Can not find domain with given name {domain_name} ')
                    print('Unable to create workflow')
                    raise Exception("Unable to create workflow")
            wf_client_obj.logger.info('domainId {}'.format(existing_domain_id))
            return existing_domain_id

    def get_existing_pipeline_id(self,wf_client_obj,domain_id,pipeline_name):
        existing_pipeline_id = None
        if domain_id is not None:
            pipelines_url_base = list_pipelines_url(wf_client_obj.client_config,domain_id=domain_id)
            filter_condition = IWUtils.ejson_serialize({"name": pipeline_name})
            pipelines_url = pipelines_url_base + f"?filter={{filter_condition}}".format(filter_condition=filter_condition)
            response = requests.request("GET", pipelines_url, headers={
                'Authorization': 'Bearer ' + wf_client_obj.client_config["bearer_token"],
                'Content-Type': 'application/json'}, verify=False)
            if response.status_code == 406:
                headers = wf_client_obj.regenerate_bearer_token_if_needed(
                    {'Authorization': 'Bearer ' + wf_client_obj.client_config["bearer_token"],
                     'Content-Type': 'application/json'})
                response = requests.request("GET", pipelines_url, headers=headers, verify=False)
            if response is not None:
                result = response.json().get("result", [])
                if len(result) > 0:
                    existing_pipeline_id = result[0]["id"]
                else:
                    wf_client_obj.logger.error('Can not find pipeline with given name {} '.format(pipeline_name))
                    wf_client_obj.logger.error('Unable to create workflow')
                    print(f'Can not find pipeline with given name {pipeline_name} ')
                    print('Unable to create workflow')
                    raise Exception("Unable to create workflow")
            wf_client_obj.logger.info('pipeline_id {}'.format(existing_pipeline_id))
            return existing_pipeline_id

    def set_active_pipeline_version_id(self,wf_client_obj):
        for mapping in self.configuration_obj["configuration"]["iw_mappings"]:
            if mapping["entity_type"] == "pipeline":
                domain_name = mapping["recommendation"]["domain_name"]
                pipeline_name = mapping["recommendation"]["pipeline_name"]
                domain_id = self.get_existing_domain_id(wf_client_obj, domain_name)
                pipeline_id = self.get_existing_pipeline_id(wf_client_obj, domain_id, pipeline_name=pipeline_name)
                filter_condition = IWUtils.ejson_serialize({"is_active": True})
                pipeline_active_version_url = list_pipeline_versions_url(wf_client_obj.client_config,domain_id=domain_id,pipeline_id=pipeline_id) + f"?filter={{filter_condition}}".format(filter_condition=filter_condition)
                response = requests.request("GET", pipeline_active_version_url,
                                            headers={'Authorization': 'Bearer ' + wf_client_obj.client_config[
                                                'bearer_token'],
                                                     'Content-Type': 'application/json'}, verify=False)
                if response.status_code == 406:
                    wf_client_obj.client_config['bearer_token'] = get_bearer_token(
                        wf_client_obj.client_config["protocol"],
                        wf_client_obj.client_config["ip"],
                        wf_client_obj.client_config["port"],
                        wf_client_obj.client_config["refresh_token"])
                    headers = IWUtils.get_default_header_for_v3(wf_client_obj.client_config['bearer_token'])
                    response = requests.request("GET", pipeline_active_version_url,
                                                headers=headers, verify=False)
                if response is not None:
                    pipeline_versions_result = response.json().get("result", [])
                    if pipeline_versions_result:
                        pipeline_version_id=pipeline_versions_result[0]["version"]
                        mapping["selected_versions"][0]["version"] = pipeline_version_id
                wf_client_obj.logger.info(response.json())
                print(response.json())

    def create(self, wf_client_obj, domain_id, domain_name):
        # update the active version of pipeline
        self.set_active_pipeline_version_id(wf_client_obj)
        sources_in_wfs = []
        workflow_name = self.configuration_obj["configuration"]["entity"]["entity_name"]
        for item in self.configuration_obj["configuration"]["iw_mappings"]:
            if item["entity_type"] == "table_group" and "source_name" in item["recommendation"]:
                sources_in_wfs.append(item["recommendation"].get("source_name"))
        filter_condition = IWUtils.ejson_serialize({"name": {"$in": sources_in_wfs}})
        source_list_url = list_sources_url(wf_client_obj.client_config)
        wf_client_obj.logger.info(f"Listing source url {source_list_url}")
        src_list_url = source_list_url + f"?filter={{filter_condition}}".format(filter_condition=filter_condition)
        response = requests.request("GET", src_list_url,
                                    headers={'Authorization': 'Bearer ' + wf_client_obj.client_config['bearer_token'],
                                             'Content-Type': 'application/json'}, verify=False)
        if response.status_code == 406:
            wf_client_obj.client_config['bearer_token'] = get_bearer_token(wf_client_obj.client_config["protocol"],
                                                                           wf_client_obj.client_config["ip"],
                                                                           wf_client_obj.client_config["port"],
                                                                           wf_client_obj.client_config["refresh_token"])
            headers = IWUtils.get_default_header_for_v3(wf_client_obj.client_config['bearer_token'])
            response = requests.request("GET", src_list_url,
                                        headers=headers, verify=False)
        wf_client_obj.logger.info(response.json())
        print(response.json())
        temp_src_ids = []
        if response.status_code == 200 and len(response.json().get("result", [])) > 0:
            result = response.json().get("result", [])
            for item in result:
                temp_src_ids.append(item["id"])
        sourceids_in_wfs = list(set(temp_src_ids))
        user_email = self.configuration_obj["user_email"]
        current_user_token = wf_client_obj.client_config.get("bearer_token","")
        parts = current_user_token.split('.')
        bearer_token_string= parts[1]
        bearer_token_string += '=' * (4 - len(parts[1]) % 4)
        bearer_token_string = base64.b64decode(bearer_token_string)
        bearer_token_json = json.loads(bearer_token_string)
        bearer_token_json = json.loads(bearer_token_json.get("sub","{}"))
        user_email = bearer_token_json.get("email",user_email)
        domain_obj = Domain(None)
        new_workflow_id = ''
        final_domain_id = None
        if domain_id is None and domain_name is None:
            wf_client_obj.logger.error('Either domainId or domain Name is required to create workflow.')
            print('Either domainId or domain Name is required to create workflow.')
            sys.exit(-1)
        if domain_name is not None and domain_id is None:
            domains_url_base = list_domains_url(wf_client_obj.client_config)
            filter_condition = IWUtils.ejson_serialize({"name": domain_name})
            domains_url = domains_url_base + f"?filter={{filter_condition}}".format(filter_condition=filter_condition)
            response = requests.request("GET", domains_url, headers={
                'Authorization': 'Bearer ' + wf_client_obj.client_config["bearer_token"],
                'Content-Type': 'application/json'}, verify=False)
            if response.status_code == 406:
                headers = wf_client_obj.regenerate_bearer_token_if_needed(
                    {'Authorization': 'Bearer ' + wf_client_obj.client_config["bearer_token"],
                     'Content-Type': 'application/json'})
                response = requests.request("GET", domains_url, headers=headers, verify=False)
            existing_domain_id = None
            if response is not None:
                result = response.json().get("result", [])
                if len(result) > 0:
                    existing_domain_id = result[0]["id"]
                    final_domain_id = existing_domain_id
                else:
                    wf_client_obj.logger.error('Can not find domain with given name {} '.format(domain_name))
                    wf_client_obj.logger.error('Unable to create workflow')
                    print(f'Can not find domain with given name {domain_name} ')
                    print('Unable to create workflow')
                    raise Exception("Unable to create workflow")
                    # wf_client_obj.logger.info('Creating a domain with given name {} '.format(domain_name))
                    # domain_id_new = domain_obj.create(wf_client_obj, domain_name)
                    # print('New domain id' + domain_id_new)
                    # final_domain_id = domain_id_new
            wf_client_obj.logger.info('domainId {}'.format(existing_domain_id))
            print(f"domainId:{existing_domain_id}")
        else:
            final_domain_id = domain_id
        wf_client_obj.logger.info('Adding user {} to domain {}'.format(user_email, final_domain_id))
        print(f'Adding user {user_email} to domain {final_domain_id}')
        domain_obj.add_user_to_domain(wf_client_obj, final_domain_id, None, user_email)
        wf_client_obj.logger.info('Adding sources {} to domain {}'.format(sourceids_in_wfs, final_domain_id))
        print(f'Adding sources {sourceids_in_wfs} to domain {final_domain_id}')
        domain_obj.add_sources_to_domain(wf_client_obj, final_domain_id, sourceids_in_wfs)
        url_for_creating_workflow = create_workflow_url(wf_client_obj.client_config, final_domain_id)
        workflow_json_object = {
            "name": workflow_name
        }
        wf_client_obj.logger.info('URL to create workflow: ' + url_for_creating_workflow)
        json_string = IWUtils.ejson_serialize(workflow_json_object)
        wf_client_obj.logger.debug(json_string)
        if json_string is not None:
            try:
                response = requests.post(url_for_creating_workflow, data=json_string,
                                         headers={
                                             'Authorization': 'Bearer ' + wf_client_obj.client_config['bearer_token'],
                                             'Content-Type': 'application/json'}, verify=False)
                if response.status_code == 406:
                    wf_client_obj.client_config['bearer_token'] = get_bearer_token(
                        wf_client_obj.client_config["protocol"],
                        wf_client_obj.client_config["ip"],
                        wf_client_obj.client_config["port"],
                        wf_client_obj.client_config["refresh_token"])
                    headers = IWUtils.get_default_header_for_v3(wf_client_obj.client_config['bearer_token'])
                    response = requests.post(url_for_creating_workflow, data=json_string, headers=headers, verify=False)
                response = IWUtils.ejson_deserialize(response.content)
                wf_client_obj.logger.debug(response)
                result = response.get('result', None)
                wf_client_obj.logger.info("result is: " + str(result))
                if result is None:
                    wf_client_obj.logger.info(
                        'Cant create workflow. {} {}'.format(response.get('message'), response.get('details')))
                    print('Cant create workflow. {} {}'.format(response.get('message'), response.get('details')))
                    wf_client_obj.logger.info('Getting the existing workflow ID with given name.')
                    print('Getting the existing workflow ID with given name.')
                    workflow_base_url = create_workflow_url(wf_client_obj.client_config, final_domain_id)
                    filter_condition = IWUtils.ejson_serialize({"name": workflow_name})
                    workflow_get_url = workflow_base_url + f"?filter={{filter_condition}}".format(
                        filter_condition=filter_condition)
                    response = requests.request("GET", workflow_get_url, headers={
                        'Authorization': 'Bearer ' + wf_client_obj.client_config['bearer_token'],
                        'Content-Type': 'application/json'}, verify=False)
                    if response.status_code == 406:
                        wf_client_obj.client_config['bearer_token'] = get_bearer_token(
                            wf_client_obj.client_config["protocol"],
                            wf_client_obj.client_config["ip"],
                            wf_client_obj.client_config["port"],
                            wf_client_obj.client_config["refresh_token"])
                        headers = IWUtils.get_default_header_for_v3(wf_client_obj.client_config['bearer_token'])
                        response = requests.request("GET", workflow_get_url, headers=headers, verify=False)
                    wf_client_obj.logger.debug(response)
                    print(response)
                    existing_workflow_id = None
                    if response.status_code == 200 and len(response.json().get("result", [])) > 0:
                        existing_workflow_id = response.json().get("result", [])[0]["id"]
                        wf_client_obj.logger.info("Workflow ID found {}".format(existing_workflow_id))
                        print("Workflow ID found {}".format(existing_workflow_id))
                    if existing_workflow_id:
                        new_workflow_id = str(existing_workflow_id)
                else:
                    new_workflow_id = result.get('id')
            except Exception as ex:
                wf_client_obj.logger.error('Response from server: {}'.format(str(ex)))
                print('Response from server: {}'.format(str(ex)))

        return new_workflow_id, final_domain_id

    def configure(self, wf_client_obj, workflow_id, domain_id):
        """
        Import workflow configuration, then activate the newest workflow version using
        POST/PUT /workflows/{wf_id}/versions/{version_id}/set-active.
        Handles 406 -> token refresh, paginated versions, and verifies activation with backoff.
        """
        import time
        import_config_status = []

        # ----- helpers -----
        def _headers():
            h = IWUtils.get_default_header_for_v3(wf_client_obj.client_config['bearer_token'])
            h.setdefault('Content-Type', 'application/json')
            h.setdefault('Accept', 'application/json')
            return h

        def _refresh_token():
            wf_client_obj.client_config['bearer_token'] = get_bearer_token(
                wf_client_obj.client_config["protocol"],
                wf_client_obj.client_config["ip"],
                wf_client_obj.client_config["port"],
                wf_client_obj.client_config["refresh_token"]
            )

        def _req(method, url, **kwargs):
            """
            One-shot request with 406 -> token refresh -> retry once.
            Ensures headers + verify=False unless provided.
            """
            kv = dict(kwargs)
            hdrs = kv.pop('headers', None) or _headers()
            verify = kv.pop('verify', False)
            resp = requests.request(method, url, headers=hdrs, verify=verify, **kv)
            if resp.status_code == 406:
                _refresh_token()
                hdrs = _headers()
                resp = requests.request(method, url, headers=hdrs, verify=verify, **kv)
            return resp

        def _get_active_version_id(wf_obj_json):
            """
            Be liberal in what we accept; different builds shape the response differently.
            """
            wf_obj = wf_obj_json or {}
            return (
                    (wf_obj.get("workflow", {}) or {}).get("active_version_id")
                    or wf_obj.get("active_version_id")
                    or (wf_obj.get("configs", {}) or {}).get("workflow_model", {}).get("active_version_id")
                    or (wf_obj.get("workflow_model", {}) or {}).get("active_version_id")
            )

        def _list_all_versions(versions_url):
            """
            Follow pagination to collect all versions. Uses limit/offset since the API
            returns 'links.next'. Falls back to offset stepping even if 'next' is present.
            """
            all_versions = []
            limit = 200
            offset = 0
            while True:
                page_url = f"{versions_url}?limit={limit}&offset={offset}"
                v_resp = _req("GET", page_url)
                v_resp.raise_for_status()
                payload = v_resp.json() or {}
                batch = payload.get("result", []) or []
                all_versions.extend(batch)

                links = payload.get("links", {}) or {}
                next_link = links.get("next")
                if not next_link or not batch:
                    break
                offset += limit
            return all_versions

        # ----- 1) import / config-migration -----
        url_for_importing_workflow = configure_workflow_url(wf_client_obj.client_config, domain_id, workflow_id)
        import_body = {
            "configuration": self.configuration_obj["configuration"],
            "dry_run": False,
            "import_configs": {
                "map_active_version": True
            }
        }

        data = IWUtils.ejson_serialize(import_body)
        response = _req("PUT", url_for_importing_workflow, data=data)
        status_code = response.status_code

        # Use IWUtils to deserialize (cluster may not set JSON headers consistently)
        try:
            response_json = IWUtils.ejson_deserialize(response.content)
        except Exception:
            response_json = {"message": response.text}

        # collect iw_mappings errors (if any)
        error = []
        for iw_mapping in response_json.get("result", {}).get("configuration", {}).get("iw_mappings", []):
            import_error = iw_mapping.get("error", "")
            if import_error:
                error.append(import_error)

        workflow_import_status = "SUCCESS" if (not error and status_code == 200) else "FAILED"
        workflow_import_response = response_json if (
                    workflow_import_status == "SUCCESS" or status_code != 200) else error
        import_config_status.append(('workflow_import_status', workflow_import_status, workflow_import_response))

        # ----- 2) activate newest version via versions/{id}/set-active -----
        if workflow_import_status == "SUCCESS":
            try:
                base_wf_url = create_workflow_url(wf_client_obj.client_config,
                                                  domain_id)  # .../v3/domains/{d}/workflows
                wf_obj_url = f"{base_wf_url}/{workflow_id}"
                versions_url = f"{wf_obj_url}/versions"

                # a) list *all* versions (pagination-aware)
                versions = _list_all_versions(versions_url)
                if not versions:
                    raise Exception("No workflow versions returned by API")

                # b) pick the true latest across all pages
                latest = max(versions, key=lambda v: (v.get('version', 0), str(v.get('created_at', ''))))
                latest_num = latest.get('version')
                latest_id = latest.get('id') or latest.get('version_id')
                if not latest_id:
                    raise Exception("Couldn't resolve version_id for the newest workflow version")

                # c) short-circuit if already active
                if latest.get("is_active", False):
                    import_config_status.append((
                        'workflow_version',
                        'SUCCESS',
                        {'activated_version': latest_num, 'already_active': True}
                    ))
                else:
                    # d) canonical activation endpoint on your cluster
                    set_url = f"{wf_obj_url}/versions/{latest_id}/set-active"
                    r = _req("POST", set_url)
                    if r.status_code in (404, 405):  # some builds only accept PUT
                        r = _req("PUT", set_url)
                    r.raise_for_status()

                    # e) verify with small retry (eventual consistency)
                    active_ok = False
                    last_active_id = None
                    for attempt in range(6):
                        # read workflow object (most direct)
                        wr = _req("GET", wf_obj_url)
                        if wr.ok:
                            wf_obj_result = (wr.json() or {}).get("result", {})
                            active_id = _get_active_version_id(wf_obj_result)
                            last_active_id = str(active_id) if active_id is not None else None
                            if last_active_id and last_active_id == str(latest_id):
                                active_ok = True
                                break

                        # fallback: list active versions
                        vr = _req("GET", f"{versions_url}?filter=%7B%22is_active%22:true%7D&limit=10")
                        if vr.ok:
                            active_versions = (vr.json() or {}).get("result", []) or []
                            if any(v.get('id') == latest_id for v in active_versions):
                                active_ok = True
                                break

                        time.sleep(1.5 + 0.5 * attempt)

                    if not active_ok:
                        # gather a little context for logs
                        v2 = _req("GET", versions_url)
                        seen_ids = [v.get('id') for v in ((v2.json() or {}).get("result", []) if v2.ok else [])]
                        raise Exception(
                            f"Activation didn't reflect yet: active_version_id={last_active_id}, "
                            f"expected={latest_id}. Versions_seen={seen_ids}"
                        )

                    import_config_status.append((
                        'workflow_version',
                        'SUCCESS',
                        {'activated_version': latest_num, 'activated_via': 'versions/{id}/set-active'}
                    ))

            except Exception as ex:
                import_config_status.append(('workflow_version', 'FAILED', str(ex)))

        # ----- 3) logging + return -----
        wf_client_obj.logger.info(response_json)
        print(response_json)
        if response_json is not None:
            wf_client_obj.logger.info((response_json.get("message") or "") + " Done")
            print((response_json.get("message") or "") + " Done")

        return workflow_import_status, import_config_status