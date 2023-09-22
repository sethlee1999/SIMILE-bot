# chat completion by using openai gpt 3.5
import json
import openai


def send_request(schema, description):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Generate the modified version of JSON value.\n You must format your output as a JSON value that "
                            "adheres to a given 'JSON Schema' instance.\n'JSON Schema' is a declarative language that allows "
                            "you to annotate and validate JSON documents.\nFor example, the example 'JSON Schema' instance {{"
                            "'properties': {{'foo': {{'description': 'a list of test words', 'type': 'array', 'items': {{"
                            "'type': 'string'}}}}}}, 'required': ['foo']}}}}\nwould match an object with one required "
                            "property, 'foo'. The 'type' property specifies 'foo' must be an 'array', and the 'description' "
                            "property semantically describes it as 'a list of test words'. The items within 'foo' must be "
                            "strings.\n Thus, the object {{'foo': ['bar', 'baz']}} is a well-formatted instance of this "
                            "example 'JSON Schema'. The object {{'properties': {{'foo': ['bar', 'baz']}}}} is not "
                            "well-formatted.\n Your output will be parsed and type-checked according to the provided schema "
                            "instance, so make sure all fields in your output match exactly!\n Here is the JSON Schema "
                            "instance your output must adhere to:\n '''json \n " + json.dumps(schema) + " \n ''' \n"},
                {"role": "user", "content": "Description: " + description}
            ],
            temperature=0,
        )
        return json.loads(response['choices'][0]['message']['content']), response['usage']['total_tokens']
    # if json dump error
    except json.decoder.JSONDecodeError:
        return 'JSON dump error', -1


if __name__ == '__main__':
    schema = {'type': 'object',
               'properties': {'checked': {'type': 'boolean', 'description': 'whether or not there is algae'},
                              'extension': {'type': 'int',
                                            'description': 'the extension of the algae\n1,less than 5 sqm\n2, 5 to 20 sqm\n3, greater than 20 sqm\n-1,not mentioned or not any of them'},
                              'look': {'type': 'int',
                                       'description': '1,Scattered\n2,Compact\n3,Grouped\n4,Surfaces tripes\n-1,not mentioned or not any of them'},
                              'colour': {'type': 'int',
                                         'description': 'the colour of the algae,1,Red\n2,Blue\n3,Green\n4,Grey\n5,Brown\n-1,not mentioned'}},
               'required': ['checked', 'extension', 'look', 'colour'], 'additionalProperties': False,
               '$schema': 'http://json-schema.org/draft-07/schema#'}
    result = send_request(schema, description='algae has red color and an extension about 12 square meters with grouped looking')
    print(result[0])
