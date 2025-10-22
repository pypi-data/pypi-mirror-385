import copy

import src.web_interface.whitelist_parsing as whitelist_parsing
import src.web_interface.wi_utils as wi_utils
import datetime
import src.utils as utils

# TODO: example of format in wi_object (Keys)


def get_empty_wi_object(key_yaml, read_in_whitelists):
    """
    This function parses the keys.yaml and returns an empty object for the web
    interface.
    :return: wi_object: object containing all information from the keys.yaml
             in a format readable by the web interface
    """

    # initialize emtpy dict to save wi_object to
    wi_object = {}

    # iterate over all keys in general structure
    for key in key_yaml:

        # parse information of a key into wi_object format
        wi_object[key], whitelist_object = parse_empty(key_yaml[key], key,
                                                       key_yaml, {}, read_in_whitelists)

    # add a key 'all_factors' with an empty list as value to the object
    # the experimental factors will be saved here after input on the website
    wi_object['all_factors'] = []
    wi_object['publication_records'] = {}

    return wi_object


def parse_empty(node, pos, key_yaml, filled_object, read_in_whitelists,
                get_whitelist_object=False):
    """
    This function parses a part of the key.yaml into an object readable by the
    web-interface
    :param filled_object: a dictionary containing pre-filled information
    :param node: a part of the key.yaml that should be parsed
    :param pos: the position of the node (chained keys)
    :param key_yaml: the whole key.yaml
    :param get_whitelist_object: bool, True if whitelists should be written
                                 into a separate object, False if not, default
                                 False
    :return: part_object: an object for the web interface parsed from node
             whitelist_object: a dictionary containing all whitelists, it is
                               only filled if 'get_whitelist_object' is set to
                               True
    """

    # disable input for the keys condition_name and sample_name because they
    # are generated
    input_disabled = True if 'special_case' in node and 'generated' in \
                             node['special_case'] and \
                             node['special_case']['generated'] in \
                             ['end', 'now'] and pos.split(':')[-1] not in ['id', 'setting', 'techniques'] \
        else False

    # initialize a whitelist object to store all whitelists
    whitelist_object = {}

    # test if the value of the current node is a dictionary
    if isinstance(node['value'], dict):
        # initialize the input type with None
        input_type = None

        # special case: merge or value_unit
        if 'special_case' in node and ('merge' in node['special_case'] or
                                       'value_unit' in node['special_case']):

            # read and parse whitelist
            whitelist, whitelist_type, input_type, headers, whitelist_keys, double = \
                whitelist_parsing.parse_whitelist(pos.split(':')[-1], node,
                                                  filled_object, whitelist_object=read_in_whitelists)

            # set input type of field organism to 'organism' -> special case
            # (used to display button to confirm organism on the website)
            if pos.split(':')[-1] == 'organism':
                input_type = 'organism_name'

            # test if the whitelist should be stored in a separate object
            if get_whitelist_object:

                # special case: value_unit
                if input_type == 'value_unit':

                    # store the whitelist in the object under the key 'unit'
                    whitelist_object['unit'] = whitelist
                    whitelist = 'unit'

                # a whitelist is defined for the key
                elif whitelist is not None:

                    # save the whitelist to the object under the keyname
                    whitelist_object[pos.split(':')[-1]] = whitelist
                    whitelist = pos.split(':')[-1]

            # creation and filling of dictionary containing all necessary
            # information for one input field
            part_object = {'position': pos, 'mandatory': node['mandatory'],
                           'list': node['list'],
                           'displayName': node['display_name'],
                           'desc': utils.print_desc(node['desc'], 'html').replace('\n', '<br>'),
                           'value': None,
                           'whitelist': whitelist,
                           'whitelist_type': whitelist_type,
                           'input_type': input_type,
                           'input_disabled': input_disabled,
                           'delete_disabled': False}

            if (part_object['whitelist'] == ['True', 'False'] or part_object['whitelist'] == 'pooled') and part_object[
                'value'] is not \
                    None:
                if part_object['value']:
                    part_object['value'] = 'True'
                else:
                    part_object['value'] = 'False'
            # special case : value unit -> add key value_unit to dict
            if input_type == 'value_unit':
                part_object['value_unit'] = node['value']['unit']['value']

            # save headers and whitelist keys in the object if they are defined
            if headers is not None:
                part_object['headers'] = headers
            if whitelist_keys is not None:
                part_object['whitelist_keys'] = whitelist_keys

            # add a search info for autofill
            if input_type in ['single_autofill', 'multi_autofill']:
                part_object['search_info'] = {
                    'organism': filled_object['organism']
                    if 'organism' in filled_object else None,
                    'key_name': part_object['position'].split(':')[-1]}

        # no special case -> the value takes a dictionary and should be
        # displayed via an expandable
        else:

            # initialize variable input_fields with empty list
            # it is used to save the keys of the 'value' dictionary as input
            # fields
            input_fields = []

            # iterate over all keys in value
            for key in node['value']:

                if not ('special_case' in node['value'][key] and 'invisible' in
                        node['value'][key]['special_case'] and
                        node['value'][key]['special_case']['invisible']):

                    # call this function to create a dictionary object for all keys
                    # storing their necessary information
                    field_infos, w_object = parse_empty(
                        node['value'][key], pos + ':' + key, key_yaml,
                        filled_object, read_in_whitelists,
                        get_whitelist_object=get_whitelist_object)

                    # add the parsed input fields to the list
                    input_fields.append(field_infos)

                    # merge the whitelist object with the object from the input
                    # field
                    whitelist_object = {**whitelist_object, **w_object}

            # creation and filling of dictionary containing all necessary
            # information for one expandable with its input fields
            part_object = {'position': pos, 'mandatory': node['mandatory'],
                           'list': node['list'], 'title': node['display_name'],
                           'desc': utils.print_desc(node['desc'], 'html').replace('\n', '<br>'), 'input_fields': input_fields,
                           'original_input': copy.deepcopy(input_fields),
                           'input_disabled': input_disabled,
                           'delete_disabled': False}

            if 'special_case' in node:
                if 'group' in node['special_case']:
                    part_object['ident_key'] = f'{pos}:{node["special_case"]["group"]}'
                if 'control' in node['special_case']:
                    part_object['control'] = node['special_case']['control']

            if 'short_desc' in node:
                part_object['short_desc'] = node['short_desc']
        # test if the key takes multiple values and add the property
        # 'list_value' as a place to save those values to via the website
        if node['list'] or input_type == 'single_autofill':
            part_object['list_value'] = []

    # the key does not contain a dictionary as value
    else:
        # read and parse whitelist
        whitelist, whitelist_type, input_type, headers, whitelist_keys, double = \
            whitelist_parsing.parse_whitelist(pos.split(':')[-1], node,
                                              filled_object, whitelist_object=read_in_whitelists)

        # test if whitelists are defined and should be stored in a separate
        # object
        if get_whitelist_object and whitelist is not None:

            # set the whitelist to the name of the key if a whitelist was
            # defined
            whitelist_object[pos.split(':')[-1]] = whitelist
            whitelist = pos.split(':')[-1]

        # creation and filling of dictionary containing all necessary
        # information for one input field
        part_object = {'position': pos, 'mandatory': node['mandatory'],
                       'list': node['list'],
                       'displayName': node['display_name'],
                       'desc': utils.print_desc(node['desc'], 'html').replace('\n', '<br>'), 'value': node['value'],
                       'whitelist': whitelist,
                       'whitelist_type': whitelist_type,
                       'input_type': input_type,
                       'input_disabled': input_disabled,
                       'delete_disabled': False}

        if (part_object['whitelist'] == ['True', 'False'] or part_object['whitelist'] == 'pooled') and part_object['value'] is not \
                None:
            if part_object['value']:
                part_object['value'] = 'True'
            else:
                part_object['value'] = 'False'

        # add headers and whitelist keys to the empty object if they are
        # defined
        if headers is not None:
            part_object['headers'] = headers
        if whitelist_keys is not None:
            part_object['whitelist_keys'] = whitelist_keys

        # test if the key takes multiple values or uses autofill and add the
        # property 'list_value' as a place to save those values to via the
        # website
        if node['list'] or input_type in ['single_autofill', 'restricted_short_text']:
            part_object['list_value'] = []

        if input_type == 'restricted_short_text':

            # default
            part_object['restriction'] = {'regex': ' ',
                                          'max_length': 10}

            if 'special_case' in node and 'restriction' in node['special_case']:
                if 'regex' in node['special_case']['restriction']:
                    part_object['restriction']['regex'] = \
                        node['special_case']['restriction']['regex']
                if 'max_length' in node['special_case']['restriction']:
                    part_object['restriction']['max_length'] = \
                        node['special_case']['restriction']['max_length']

        # add the key 'search_info' to all fields using autofill to help get
        # the correct whitelist via the website
        if input_type == 'single_autofill' or input_type == 'multi_autofill':
            part_object['search_info'] = {
                'organism': filled_object['organism']
                if 'organism' in filled_object else None,
                'key_name': part_object['position'].split(':')[-1]}

        if input_type == 'date':
            part_object['value'] = wi_utils.str_to_date(datetime.datetime.now().strftime('%d.%m.%Y'))

    return part_object, whitelist_object
