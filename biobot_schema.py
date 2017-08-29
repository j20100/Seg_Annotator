#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""This file contains the JSON Schemas used in the protocol and deck editors."""

def get_schema(value, conf, biobot):
    schema = {}

    if value == 'labware':
        # Get validated labware names and types only
        schema = list(biobot.deck.find({'validated': True}, {'name': 1, 'type': 1, '_id': 0}))

    elif value == 'instructions':
        generated = 'This is automatically generated from the previous two fields'
        pattern_description = 'Must be one or two uppercase letter followed by one or two digit'

        # Tools dictionnaries are defined as separate variables to prevet code duplication

        # Pipette Tools section
        from_dict = {
            'from_container': {
                'title': 'From (container)',
                'type': 'string',
                'pattern': '^(?!\s*$).+',
                'propertyOrder': 1
            },
            'from_location': {
                'title': 'From (location)',
                'type': 'string',
                'pattern': '^[A-Z]{1,2}[0-9]{1,2}$',
                'description': pattern_description,
                'propertyOrder': 2
            },
            'from': {
                'title': 'From',
                'type': 'string',
                'description': generated,
                'template': '{{f_con}}/{{f_loc}}',
                'watch': {
                    'f_con': 'id.from_container',
                    'f_loc': 'id.from_location'
                },
                'propertyOrder': 3
            }
        }

        to_dict = {
            'to_container': {
                'title': 'to (container)',
                'type': 'string',
                'pattern': '^(?!\s*$).+',
                'propertyOrder': 4
            },
            'to_location': {
                'title': 'to (location)',
                'type': 'string',
                'pattern': '^[A-Z]{1,2}[0-9]{1,2}$',
                'description': pattern_description,
                'propertyOrder': 5
            },
            'to': {
                'title': 'To',
                'type': 'string',
                'description': generated,
                'template': '{{t_con}}/{{t_loc}}',
                'watch': {
                    't_con': 'id.to_container',
                    't_loc': 'id.to_location'
                },
                'propertyOrder': 6
            }
        }

        volume_dict = {
            'volume': {
                'title': 'Volume (µL)',
                'type': 'number',
                'minimum': 0,
                'propertyOrder': 7
            }
        }

        iteration_dict = {
            'iteration': {
                'title': 'Iterations',
                'type': 'integer',
                'minimum': 1,
                'default': 1,
                'propertyOrder': 8
            }
        }

        mix_iteration_dict = {
            'mix_iteration': {
                'title': 'Mix iterations',
                'type': 'integer',
                'minimum': 1,
                'default': 1,
                'propertyOrder': 9
            }
        }

        aspirate_dict = {
            'aspirate_speed': {
                'title': 'Aspirate speed (µL/s)',
                'type': 'number',
                'minimum': 1,
                'default': conf.default_pipette_speed,
                'propertyOrder': 10
            }
        }

        dispense_dict = {
            'dispense_speed': {
                'title': 'Dispense speed (µL/s)',
                'type': 'number',
                'minimum': 1,
                'default': conf.default_pipette_speed,
                'propertyOrder': 11
            }
        }

        transfer = {
            'title': 'Transfer',
            'description': 'Transfer a volume of liquid from one location to another.',
            'type': 'object',
            'id': 'id',
            'properties': {}
        }

        # Add pipette transfer properties
        transfer_properties = [from_dict, to_dict, volume_dict, aspirate_dict, dispense_dict]
        for prop in transfer_properties:
            transfer['properties'].update(prop)

        mix = {
            'title': 'Mix',
            'description': 'Mix liquid in place by aspiring and dispensing a specific volume one or more times.',
            'type': 'object',
            'id': 'id',
            'properties': {}
        }

        # Add pipette mix properties
        mix_properties = [from_dict, volume_dict, iteration_dict, aspirate_dict, dispense_dict]
        for prop in mix_properties:
            mix['properties'].update(prop)

        serial_dilution = {
            'title': 'Serial dilution',
            'description': 'Perform a serial dilution by mixing and transferring liquids over multiple wells.',
            'type': 'object',
            'id': 'id',
            'properties': {}
        }

        # Add pipette serial dilution properties
        serial_dilution_properties = [from_dict, to_dict, volume_dict, iteration_dict, mix_iteration_dict, aspirate_dict, dispense_dict]
        for prop in serial_dilution_properties:
            serial_dilution['properties'].update(prop)

        multi_dispense = {
            'title': 'Multi dispense',
            'description': 'Dispense a specific volume of liquid over multiple wells.',
            'type': 'object',
            'id': 'id',
            'properties': {}
        }

        # Add pipette multi dispense properties
        multi_dispense_properties = [from_dict, to_dict, volume_dict, iteration_dict, aspirate_dict, dispense_dict]
        for prop in multi_dispense_properties:
            multi_dispense['properties'].update(prop)

        pipette_groups = {
            'title': 'Actions',
            'type': 'array',
            'format': 'tabs',
            'maxItems': conf.max_actions_per_group,
            'items': {
                'title': 'Action',
                'type': 'object',
                'oneOf': [
                    {
                        'title': 'Transfer',
                        'properties': {
                            'transfer': transfer
                        },
                    },
                    {
                        'title': 'Mix',
                        'properties': {
                            'mix': mix
                        },
                    },
                    {
                        'title': 'Serial dilution',
                        'properties': {
                            'serial_dilution': serial_dilution
                        },
                    },
                    {
                        'title': 'Multi dispense',
                        'properties': {
                            'multi_dispense': multi_dispense
                        },
                    }
                ]
            }
        }

        pipette_s = {
            'title': 'Single Pipette',
            'properties': {
                'op': {
                    'title': 'Tool',
                    'type': 'string',
                    'enum': ['pipette_s'],
                    'propertyOrder': 1
                },
                'groups': pipette_groups
            }
        }

        pipette_m = {
            'title': 'Multiple Pipette',
            'properties': {
                'op': {
                    'title': 'Tool',
                    'type': 'string',
                    'enum': ['pipette_m'],
                    'propertyOrder': 1
                },
                'groups': pipette_groups
            }
        }

        # Gripper Tool section
        move = {
            'title': 'Move',
            'description': 'Move an object from a location to another.',
            'type': 'object',
            'id': 'id',
            'properties': {}
        }

        # Add gripper move properties
        move_properties = [from_dict, to_dict]
        for prop in move_properties:
            move['properties'].update(prop)

        gripper_groups = {
            'title': 'Actions',
            'type': 'array',
            'format': 'tabs',
            'maxItems': conf.max_actions_per_group,
            'items': {
                'title': 'Action',
                'type': 'object',
                'oneOf': [
                    {
                        'title': 'Move',
                        'properties': {
                            'move': move
                        },
                    }
                ]
            }
        }

        gripper = {
            'title': 'Gripper',
            'properties': {
                'op': {
                    'title': 'Tool',
                    'type': 'string',
                    'enum': ['gripper'],
                    'propertyOrder': 1
                },
                'groups': gripper_groups
            }
        }

        # Petri Dish section
        picking_criterias = [
            {
                'title': 'Color',
                'properties': {
                    'category': {
                        'title': 'Type of criteria',
                        'type': 'string',
                        'enum': ['color'],
                        'propertyOrder': 1
                    },
                    'color': {
                        'title': 'Color',
                        'type': 'string',
                        'format': 'color',
                        'default': '#216bf5',
                        'propertyOrder': 2
                    },
                }
            },
            {
                'title': 'Size',
                'properties': {
                    'category': {
                        'title': 'Type of criteria',
                        'type': 'string',
                        'enum': ['size'],
                        'propertyOrder': 1
                    },
                    'minimum': {
                        'title': 'Minimum size (mm²)',
                        'type': 'number',
                        'minimum': 0,
                        'propertyOrder': 2
                    },
                    'maximum': {
                        'title': 'Maximum size (mm²)',
                        'type': 'number',
                        'minimum': 0,
                        'propertyOrder': 3
                    }
                }
            },
            {
                'title': 'Excentricity',
                'description': 'An excentricity of 0 is a perfect circle.',
                'properties': {
                    'category': {
                        'title': 'Type of criteria',
                        'type': 'string',
                        'enum': ['excentricity'],
                        'propertyOrder': 1
                    },
                    'minimum': {
                        'title': 'Minimum excentricity',
                        'type': 'number',
                        'minimum': 0,
                        'maximum': 1,
                        'default': 0,
                        'propertyOrder': 2
                    },
                    'maximum': {
                        'title': 'Maximum excentricity',
                        'type': 'number',
                        'minimum': 0,
                        'maximum': 1,
                        'default': 1,
                        'propertyOrder': 3
                    }
                }
            },
            {
                'title': 'Perimeter',
                'properties': {
                    'category': {
                        'title': 'Type of criteria',
                        'type': 'string',
                        'enum': ['perimeter'],
                        'propertyOrder': 1
                    },
                    'minimum': {
                        'title': 'Minimum perimeter (mm)',
                        'type': 'number',
                        'minimum': 0,
                        'propertyOrder': 2
                    },
                    'maximum': {
                        'title': 'Maximum perimeter (mm)',
                        'type': 'number',
                        'minimum': 0,
                        'propertyOrder': 3
                    }
                }
            },
            {
                'title': 'Segmentation',
                'description': 'Default is false, even if criteria is not selected.',
                'properties': {
                    'category': {
                        'title': 'Type of criteria',
                        'type': 'string',
                        'enum': ['segmentation'],
                        'propertyOrder': 1
                    },
                    'segment': {
                        'title': 'Segment adjascent colonies for picking?',
                        'type': 'boolean',
                        'default': False,
                        'propertyOrder': 2
                    }
                }
            }
        ]

        colony_picking = {
            'action': {
                'title': 'Action',
                'type': 'string',
                'enum': ['autopick'],
                'propertyOrder': 1
            },
            'to_container': {
                'title': 'To (container)',
                'description': 'Must be a Multiwell Plate',
                'type': 'string',
                'pattern': '^(?!\s*$).+',
                'propertyOrder': 2
            },
            'to_location': {
                'title': 'To (location)',
                'type': 'string',
                'pattern': '^[A-Z]{1,2}[0-9]{1,2}$',
                'description': pattern_description,
                'propertyOrder': 3
            },
            'to': {
                'title': 'To',
                'type': 'string',
                'description': generated,
                'template': '{{f_con}}/{{f_loc}}',
                'watch': {
                    'f_con': 'id.to_container',
                    'f_loc': 'id.to_location'
                },
                'propertyOrder': 4
            },
            'number': {
                'title': 'Number of colonies to pick',
                'type': 'integer',
                'minimum': 0,
                'default': 0,
                'propertyOrder': 5
            },
            'criterias': {
                'title': 'Criterias',
                'type': 'array',
                'format': 'tabs',
                'minItems': 1,
                'propertyOrder': 6,
                'items': {
                    'title': 'Criteria',
                    'type': 'object',
                    'headerTemplate': '{{self.category}}',
                    'oneOf': picking_criterias
                }
            }
        }

        petri_analysis_groups = {
            'title': 'Actions',
            'type': 'array',
            'format': 'tabs',
            'items': {
                'title': 'Action',
                'type': 'object',
                'id': 'id',
                'headerTemplate': '{{i}} - {{self.action}}',
                'oneOf': [
                    {
                        'title': 'Bacterial Colony Analysis',
                        'description': 'Analyze a Petri dish to extract the characteristics of the bacterial colonies.',
                        'properties': {
                            'action': {
                                'title': 'Action',
                                'type': 'string',
                                'enum': ['analyze']
                            }
                        },
                    },
                    {
                        'title': 'Colony Picking',
                        'description': 'Use one or more criterias to pick specific bacterial colonies and make them grow in another location.',
                        'properties': colony_picking
                    }
                ]
            }
        }

        petri_analysis = {
            'title': 'Petri Dish',
            'properties': {
                'op': {
                    'title': 'Petri Dish Analysis',
                    'type': 'string',
                    'enum': ['2d_camera'],
                    'propertyOrder': 1
                },
                'name': {
                    'title': 'Petri Dish Name',
                    'type': 'string',
                    'propertyOrder': 2
                },
                'light': {
                    'title': 'Backlight color',
                    'type': 'string',
                    'enum': ['white', 'blue'],
                    'propertyOrder': 3
                },
                'groups': petri_analysis_groups
            }
        }

        # Instructions JSON schema
        schema = {
            'title': 'Instructions',
            'type': 'array',
            'format': 'tabs',
            'maxItems': conf.max_protocol_steps,
            'items': {
                'title': 'Step',
                'type': 'object',
                'headerTemplate': '{{i}} - {{self.op}}',
                'anyOf': [
                    pipette_s,
                    pipette_m,
                    gripper,
                    petri_analysis
                ]
            }
        }

    elif value == 'deck':
        # Deck editor schema
        deck_cursor = biobot.labware.find({'class': {'$ne': 'Tool'}})
        deck = sorted([item['type'] for item in deck_cursor])

        schema = {
            'title': 'Deck',
            'type': 'array',
            'format': 'tabs',
            'maxItems': conf.max_labware_items,
            'uniqueItems': True,
            'items': {
                'title': 'Item',
                'headerTemplate': '{{self.type}} - {{self.name}} ({{self.row}}{{self.col}})',
                'type': 'object',
                'properties': {
                    'type': {
                        'title': 'Type',
                        'type': 'string',
                        'enum': deck,
                        'propertyOrder': 1
                    },
                    'name': {
                        'title': 'Name',
                        'type': 'string',
                        'description': 'Must not be empty',
                        'pattern': '^(?!\s*$).+',
                        'propertyOrder': 2
                    },
                    'row': {
                        'title': 'Location (row)',
                        'type': 'string',
                        'description': 'A-Z',
                        'pattern': '^[A-Z]{1}$',
                        'propertyOrder': 3
                    },
                    'col': {
                        'title': 'Location (column)',
                        'type': 'string',
                        'description': '0-99',
                        'pattern': '^[0-9]{1,2}$',
                        'propertyOrder': 4
                    }
                }
            }
        }

    elif value == 'tools':
        # Get Tools schema (from Manage Labware --> Edit tools)
        tools_cursor = biobot.labware.find({'class': 'Tool'})
        tools = sorted([item['type'] for item in tools_cursor])
        schema = {
            'title': 'Tools configuration',
            'type': 'array',
            'format': 'tabs',
            'minItems': conf.min_tools_count,
            'maxItems': len(tools),
            'uniqueItems': True,
            'items': {
                'title': 'Tool',
                'headerTemplate': '{{self.type}}',
                'type': 'object',
                'properties': {
                    'type': {
                        'title': 'Type',
                        'type': 'string',
                        'enum': tools,
                        'propertyOrder': 1
                    },
                    'offset_x': {
                        'title': 'Offset X (mm)',
                        'type': 'number',
                        'propertyOrder': 2
                    },
                    'offset_y': {
                        'title': 'Offset Y (mm)',
                        'type': 'number',
                        'propertyOrder': 3
                    },
                    'offset_z': {
                        'title': 'Offset Z (mm)',
                        'type': 'number',
                        'propertyOrder': 4
                    }
                }
            }
        }

    return schema

