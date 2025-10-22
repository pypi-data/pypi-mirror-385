import src.find_metafiles as find_metafiles
import src.utils as utils
import src.web_interface.html_output as html_output
import src.web_interface.wi_utils as wi_utils

# TODO: refactor and comment


def get_meta_info(html_str, metafiles, project_id, validation_reports):
    """
    This file creates an HTML summary for a project containing metadata
    :param project_id: the id of the project
    :return: html_str: the summary in HTML
    """
    correct_file = None
    for metafile in metafiles:
        if (
                "id" in metafile
                and metafile["id"] == project_id
        ):
            correct_file = utils.read_in_yaml(metafile['path'])
            break

    if correct_file is not None:
        html_str += f'<h2 style="text-align:center;">{project_id}</h2><hr>'
        if validation_reports is not None:
            if (
                    validation_reports["error_count"] > 0
                    or validation_reports["warning_count"] > 0
            ):
                error = None
                warning = None

                for report in validation_reports["corrupt_files"]["report"]:
                    if report["file"]["path"] == correct_file["path"]:
                        error = report["error"]
                        warning = report["warning"]
                        break

                # TODO: error Handling + Ausgabe
                if error is not None:
                    html_str += f'<font color="red"><h3><b>ERROR:</b></h3>'
                    if len(error[0]) > 0:
                        html_str += f"<b>Missing mandatory keys:</b><br>"
                        html_str += "<ul>"
                        for elem in error[0]:
                            html_str += f"<li>{elem}</li>"
                        html_str += "</ul>"
                    if len(error[1]) > 0:
                        print(error[1])
                        html_str += f"<b>Invalid keys:</b><br>"
                        html_str += "<ul>"
                        for elem in error[1]:
                            value = correct_file
                            for key in elem.split(":"):
                                if isinstance(value, list):
                                    for l_elem in value:
                                        if key in l_elem:
                                            value = l_elem[key]
                                            break
                                else:
                                    if key in value:
                                        value = value[key]
                            html_str += f"<li>{elem}: {value}</li>"
                            correct_file = wi_utils.pop_key(
                                correct_file, elem.split(":"), value
                            )
                        html_str += "</ul>"

                    if len(error[2]) > 0:
                        html_str += f"<b>Invalid entries:</b><br>"
                        html_str += "<ul>"
                        for elem in error[2]:
                            html_str += (
                                f'<li>{elem.split(":")[-1]} in '
                                f'{":".join(elem.split(":")[:-1])}</li>'
                            )
                            correct_file = wi_utils.pop_value(
                                correct_file, elem.split(":")[:-1],
                                elem.split(":")[-1]
                            )
                        html_str += "</ul>"

                    if len(error[3]) > 0:
                        html_str += f"<b>Invalid values:</b><br>"
                        html_str += "<ul>"
                        for elem in error[3]:
                            html_str += (
                                f"<li>{elem[0]}: {elem[1]} -> " f"{elem[2]}</li>"
                            )
                        html_str += "</ul>"

                    html_str += '</font><hr style="border-top: dotted 1px; background-color: transparent;" />'

                if warning is not None:
                    html_str += f'<font color="orange"><h3><b>WARNING:</b></h3>'
                    html_str += "<ul>"
                    for elem in warning:
                        message = elem[0].replace("'", "")
                        html_str += f"<li>{message}: {elem[1]}</li>"
                    html_str += "</ul>"
                    html_str += '</font><hr style="border-top: dotted 1px; background-color: transparent;" />'

        if "path" in correct_file:
            correct_file.pop("path")
        for elem in correct_file:
            end = f'{"<hr><br>" if elem != list(correct_file.keys())[-1] else ""}'
            html_str = (
                f"{html_str}<h3>{elem}</h3>"
                f"{html_output.object_to_html(correct_file[elem], 0, False)}<br>"
                f"{end}"
            )

    return html_str, correct_file


def get_search_mask(key_yaml):
    """
    This functions returns all necessary information for the search mask.
    :return: a dictionary containing all keys of the metadata structure and a
             whitelist object
    """
    keys = [
        {
            "key_name": "All keys",
            "display_name": "All Fields",
            "nested": [],
            "whitelist": False,
            "chained_keys": "",
        }
    ]
    keys += get_search_keys(key_yaml, "")
    return {"keys": keys}


def find_metadata(key_yaml, path, search_string):
    """
    This function searches for metadata files that match a search string in a
    given directory
    :param path: the path that should be searched
    :param search_string: the search string
    :return: new_files: a list containing all matching files
    """
    files = find_metafiles.find_projects(key_yaml, path, search_string, True)
    new_files = []
    for i in range(len(files)):
        for key in files[i]:
            res = {"id": key, "path": files[i][key]["path"]}
            try:
                res["project_name"] = files[i][key]["project"]["project_name"]
            except KeyError:
                res["project_name"] = None

            try:
                res["owner"] = files[i][key]["project"]["owner"]["name"]
            except KeyError:
                res["owner"] = None

            try:
                res["email"] = files[i][key]["project"]["owner"]["email"]
            except KeyError:
                res["email"] = None

            res["organisms"] = list(utils.find_keys(files[i][key], "organism_name"))

            try:
                res["description"] = files[i][key]["project"]["description"]
            except KeyError:
                res["description"] = None

            try:
                res["date"] = files[i][key]["project"]["date"]
            except KeyError:
                res["date"] = None

            if "nerd" in files[i][key]["project"]:
                nerds = []
                for nerd in files[i][key]["project"]["nerd"]:
                    nerds.append(nerd["name"])
                res["nerd"] = nerds
            else:
                res["nerd"] = None
            
            cell_type = list(set(utils.find_keys(files[i][key], 'cell_type')))
            res['cell_type'] = cell_type

            tissue = []
            
            tissues = list(utils.find_keys(files[i][key], 'tissue'))
            for elem in tissues:
                tissue += elem
            tissue = list(set(tissue))
            res['tissue'] = tissue

            # treatment
            treatment = []
            
            medical = list(utils.find_list_key(files[i][key], 'medical_treatment:treatment_type'))
            treatment += list(set(medical))
            
            physical = list(utils.find_keys(files[i][key], 'physical_treatment'))
            treatment += list(set(physical))
            
            injury = list(utils.find_list_key(files[i][key], 'injury:injury_type'))
            treatment += list(set(injury))

            res['treatment'] = treatment

            # disease

            disease = list(utils.find_list_key(files[i][key], 'disease:disease_type'))
            res['disease'] = list(set(disease))

            new_files.append(res)

    return new_files


def get_search_keys(key_yaml, chained, is_factor= False):
    """
    This function returns all keys of the metadata structure in a nested way
    :param key_yaml: the read in keys.yaml
    :param chained: the position of the key
    :return: res: a dictionary containing all metadata keys
    """
    res = []
    for key in key_yaml:
        d = {
            "key_name": key,
            "display_name": list(utils.find_keys(key_yaml, key))[0]["display_name"],
        }

        exist = True
        if (
            isinstance(key_yaml[key]["value"], dict)
            and not set(["mandatory", "list", "desc", "display_name", "value"])
            <= set(key_yaml[key]["value"].keys())
            and not (
                "special_case" in key_yaml[key]
                and "merge" in key_yaml[key]["special_case"]
            )
        ):
            if key == 'technical_replicates':
                exist = False
            else:
                d["nested"] = get_search_keys(
                    key_yaml[key]["value"],
                    f"{chained}{key}:" if chained != "" else f"{key}:",
                    True if 'samples:' in chained else False)
        else:
            if 'special_case' in key_yaml[key] and 'generated' in \
                    key_yaml[key]['special_case'] and \
                    key_yaml[key]['special_case']['generated'] in \
                    ['now', 'end'] and key != 'id' and not \
                    ('invisible' in key_yaml[key]['special_case'] and
                     key_yaml[key]['special_case']['invisible']):
                exist = False
            elif chained.endswith('experimental_factors:') and key == 'values':
                exist = False
            else:
                d["chained_keys"] = f"{chained}{key}:" if chained != "" else f"{key}:"
                d["nested"] = []

        if exist:
            if len(d['nested']) == 1:
                if key == 'experimental_factors':
                    display_name = d['display_name']
                    d = d['nested'][0]
                    d['display_name'] = display_name
                else:
                    d = d['nested'][0]
            else:
                if "whitelist" in key_yaml[key]:
                    d["whitelist"] = key_yaml[key]["whitelist"]
                elif (
                    "special_case" in key_yaml[key] and "merge" in key_yaml[key]["special_case"]
                ):
                    d["whitelist"] = key_yaml[key]["value"][
                        key_yaml[key]["special_case"]["merge"]
                    ]["whitelist"]

                if "whitelist" in d and d["whitelist"]:
                    d["search_info"] = {"key_name": key}
            if is_factor:
                display_name = chained.rstrip(':').split(':')[-1].replace('_', ' ').title()
                d['display_name'] = f'{display_name} {d["display_name"]}'
            res.append(d)
    return res
