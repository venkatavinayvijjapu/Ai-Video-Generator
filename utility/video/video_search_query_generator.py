import json
import re
import groq
from datetime import datetime
import os
from pydantic import Strict
import ast
# import json
# import re
# from datetime import datetime

# from utility.utils import log_response,LOG_TYPE_GPT

client = groq.Groq(
    # This is the default and can be omitted
    api_key='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',
)
log_directory = ".logs/gpt_logs"

prompt = """# Instructions

Given the following video script and timed captions, extract three visually concrete and specific keywords for each time segment that can be used to search for background videos. The keywords should be short and capture the main essence of the sentence. They can be synonyms or related terms. If a caption is vague or general, consider the next timed caption for more context. If a keyword is a single word, try to return a two-word keyword that is visually concrete. If a time frame contains two or more important pieces of information, divide it into shorter time frames with one keyword each. Ensure that the time periods are strictly consecutive and cover the entire length of the video. Each keyword should cover between 2-4 seconds. The output should be in JSON format, like this: [[[t1, t2], ["keyword1", "keyword2", "keyword3"]], [[t2, t3], ["keyword4", "keyword5", "keyword6"]], ...]. Please handle all edge cases, such as overlapping time segments, vague or general captions, and single-word keywords.

For example, if the caption is 'The cheetah is the fastest land animal, capable of running at speeds up to 75 mph', the keywords should include 'cheetah running', 'fastest animal', and '75 mph'. Similarly, for 'The Great Wall of China is one of the most iconic landmarks in the world', the keywords should be 'Great Wall of China', 'iconic landmark', and 'China landmark'.

Important Guidelines:

Use only English in your text queries.
Each search string must depict something visual.
The depictions have to be extremely visually concrete, like rainy street, or cat sleeping.
'emotional moment' <= BAD, because it doesn't depict something visually.
'crying child' <= GOOD, because it depicts something visual.
The list must always contain the most relevant and appropriate query searches.
['Car', 'Car driving', 'Car racing', 'Car parked'] <= BAD, because it's 4 strings.
['Fast car'] <= GOOD, because it's 1 string.
['Un chien', 'une voiture rapide', 'une maison rouge'] <= BAD, because the text query is NOT in English.
While giving text make sure you are initializing text clearly because i came across an error you provided like [ [[0, 0.7], ["Sun"s rays"] ], ... ] This is unable to process for me instead give in this way [ [[0, 0.7], ["Sun's rays"] ]].


You are needed to only generate response, don't add any phrases at beginning or ending also follow the output format as below:
Output Format or example:
```json [ [[0, 3.9], ["Interesting facts", "facts about beer", "beer facts"]], [[3.9, 6.66], ["oldest recipe", "4000 years", "ancient Mesopotamia"]], [[6.66, 7.56], ["Mesopotamian beer"]], [[7.56, 10.42], ["Czech Republic", "beer consumption", "per capita"]], [[10.42, 12.48], ["highest consumption"]], [[12.48, 15.5], ["Russia beer", "non-alcoholic"]], [[15.5, 17.1], ["Russia 2011"]], [[17.1, 22.26], ["beer foam", "beer head", "beer aroma"]], [[22.26, 22.76], ["beer flavor"]], [[22.76, 27.3], ["13th century", "beer tasters", "poison check"]], [[27.3, 28.72], ["drinking shoes"]], [[28.72, 31.26], ["most expensive", "expensive beer"]], [[31.26, 35.24], ["Shipwrecked 1907", "Heidsieck beer"]], [[35.24, 38.84], ["beer shipwreck", "500000 bottle"]] ] ```

Note: Follow my output example or fomat only don't add ay unneccessary phrases at beginning or ending, also make sure the the braces [  are correctly given.
I strictly remind you not t add any phrases at beginning or endding like Here are the visually concrete and specific keywords for each time segment: 

"""


# Log types
LOG_TYPE_GPT = "GPT"
LOG_TYPE_PEXEL = "PEXEL"

# log directory paths
DIRECTORY_LOG_GPT = ".logs/gpt_logs"
DIRECTORY_LOG_PEXEL = ".logs/pexel_logs"

# method to log response from pexel and openai
def log_response(log_type, query,response):
    log_entry = {
        "query": query,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    print(log_entry)
    if log_type == LOG_TYPE_GPT:
        if not os.path.exists(DIRECTORY_LOG_GPT):
            os.makedirs(DIRECTORY_LOG_GPT)
        filename = '{}_gpt3.txt'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        filepath = os.path.join(DIRECTORY_LOG_GPT, filename)
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(log_entry) + '\n')

    if log_type == LOG_TYPE_PEXEL:
        if not os.path.exists(DIRECTORY_LOG_PEXEL):
            os.makedirs(DIRECTORY_LOG_PEXEL)
        filename = '{}_pexel.txt'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))
        filepath = os.path.join(DIRECTORY_LOG_PEXEL, filename)
        with open(filepath, "w") as outfile:
            outfile.write(json.dumps(log_entry) + '\n')


# def fix_json(json_str):
#     # Replace smart quotes with standard double quotes
#     json_str = json_str.replace("‘", "\"").replace("’", "\"")
#     json_str = json_str.replace("“", "\"").replace("”", "\"")
    
#     # Handle escaped quotes inside strings
#     json_str = re.sub(r'(\s|^)"([^"]*?)"(\s|$)', r'\1"\2"\3', json_str)
    
#     # Fix incorrect escaping of double quotes
#     json_str = json_str.replace('"you didn\'t"', '"you didn\'t"')
    
#     # Remove any stray backslashes not used for escaping
#     json_str = re.sub(r'\\(?!["\\/bfnrtu])', '', json_str)
    
#     # Remove trailing commas in objects and arrays
#     json_str = re.sub(r',\s*(\]|\})', r'\1', json_str)
    
#     # return json_str
#     return json_str

def fix_json(json_str):
    # Replace smart quotes with standard double quotes
    json_str = json_str.replace("‘", "\"").replace("’", "\"")
    json_str = json_str.replace("“", "\"").replace("”", "\"")

    # Correct unescaped quotes in strings
    json_str = re.sub(r'(\s|^)"([^"]*?)"(\s|$)', r'\1"\2"\3', json_str)
    json_str = re.sub(r'(\w)"(\w)', r'\1"\2', json_str)  # For cases like "world"s largest"

    # Remove stray backslashes not part of escape sequences
    json_str = re.sub(r'\\(?!["\\/bfnrtu])', '', json_str)

    # Ensure all entries are within lists and fix missing commas
    json_str = re.sub(r'(\[\[\[\[.*?\]\]\]\])', lambda m: m.group(0).replace(' ', ',').replace(']]]', ']]'), json_str)

    # Ensure trailing commas in objects or arrays are removed
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

    return json_str

def getVideoSearchQueriesTimed(script, captions_timed):
    end = captions_timed[-1][0][1]
    print("1")
    try:
      
        out = [[[0, 0], ""]]
        print("2")
        while out[-1][0][1] != end:
            content = call_Groq(script, captions_timed).replace("'", '"')
            print("end")
            print("contents:",content)
            try:
                out = json.loads(content)
                print("3")
                print("out")
                print(out)
            except json.JSONDecodeError as e:
                print("Initial JSON parsing failed:", e)
                content = fix_json(content.replace("```json", "").replace("```", ""))
                try:
                    out = json.loads(content)
                except json.JSONDecodeError as e:
                    print("Second JSON parsing failed:", e)
                    return "Error: Unable to parse JSON response."
        return out
    except Exception as e:
        print("Error in response:", e)
    return None



def call_Groq(script, captions_timed):
    user_content = """Script: {}
Timed Captions: {}
""".format(script, "".join(map(str, captions_timed)))
    print("Content:", user_content)
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        temperature=1,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": user_content}
        ]
    )
    
    text = response.choices[0].message.content.strip()
    text = re.sub(r'\s+', ' ', text)  # Fix the invalid escape sequence warning
    print("Text:", text)
    print()
    print("h")
    print(LOG_TYPE_GPT)
    print("h")
    print(log_response(LOG_TYPE_GPT, script, text))  # Assuming log_response is defined elsewhere
    return text

def merge_empty_intervals(segments):
    merged = []
    i = 0
    while i < len(segments):
        interval, url = segments[i]
        if url is None:
            j = i + 1
            while j < len(segments) and segments[j][1] is None:
                j += 1
            
            if i > 0:
                prev_interval, prev_url = merged[-1]
                if prev_url is not None and prev_interval[1] == interval[0]:
                    merged[-1] = [[prev_interval[0], segments[j-1][0][1]], prev_url]
                else:
                    merged.append([interval, prev_url])
            else:
                merged.append([interval, None])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged
