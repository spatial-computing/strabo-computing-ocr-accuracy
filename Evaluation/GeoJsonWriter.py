import json


__author__ = 'Tan'


def init_output_json_structure():
    output_json = dict()
    output_json['type'] = "FeatureCollection"
    output_json['crs'] = {}
    output_json['crs']['type'] = 'name'
    output_json['crs']['properties'] = {}
    output_json['crs']['properties']['name'] = 'urn:ogc:def:crs:OGC:1.3:CRS84'
    output_json['features'] = []

    return output_json


def generate_overlap_feature(overlap_polygon, isValid=True, tag=-1):
    new_feature = dict()
    new_feature['type'] = 'Feature'
    new_feature['geometry'] = {}
    new_feature['geometry']['type'] = 'Polygon'
    new_feature['geometry']['coordinates'] = overlap_polygon.get_point_list()
    new_feature['properties'] = {}

    if isValid:
        new_feature['properties']['valid'] = 'true'
    else:
        new_feature['properties']['valid'] = 'false'

    if tag != -1:
        new_feature['properties']['id'] = tag

    return new_feature


def output_json_file(json_object, result_filename, positive=True):
    if positive:
        name = "./Overlaps/" + result_filename.split('.')[-3] + ".json"
    else:
        name = "./NonOverlaps/" + result_filename.split('.')[-3] + ".json"

    json_result_file = open(name, 'w')
    content = json.dumps(json_object)
    json_result_file.write(content)
    json_result_file.close()
