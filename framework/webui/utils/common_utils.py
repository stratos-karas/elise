import base64
import os

def get_session_dir(session_data):
    sid = session_data["sid"]
    session_stem_dir = base64.b64encode(sid.encode("utf-8")).decode("utf-8")
    session_dir = f"/tmp/{session_stem_dir}"
    return session_dir

def parse_uploaded_contents(enc_contents, content_type):
    # Decode the contents
    content_type_str, content_string = enc_contents.split(',')
    
    print(content_type)
    
    if content_type not in content_type_str.lower():
        raise Exception

    decoded = base64.b64decode(content_string)
    return decoded.decode('utf-8')

def create_twinfile(session_dir, filename, contents, content_type):
    # Create the session directory if it doesn't exist
    if not os.path.isdir(session_dir):
        os.makedirs(session_dir, exist_ok=True)
    
    # Create the twin file
    ## parse contents
    parsed_contents = parse_uploaded_contents(contents, content_type)

    ## encode filename
    suffix_start_pos = filename.rfind(".")
    name = filename[:suffix_start_pos]
    suffix = filename[suffix_start_pos+1:]
    enc_name = base64.b64encode(name.encode("utf-8")).decode("utf-8")
    enc_filename = f"{session_dir}/{enc_name}.{suffix}"

    # Write contents to new file under session's directory
    with open(enc_filename, "w") as fd:
        fd.write(parsed_contents)

    return enc_filename
