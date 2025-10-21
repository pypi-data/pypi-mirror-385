from typing import Callable
from pandas import (DataFrame,Series)
from datetime import datetime
from zoneinfo import ZoneInfo
from time import sleep
from functools import partial
import tarfile
import json
import os
from numpy import (
    asarray,
    dot
)
from numpy.linalg import norm
from itertools import chain
from graph_tool.all import (
    Graph,
    similarity,
    adjacency)


### PIPELINE FUNCTIONS

# Clean text using supplied function and calculate text length
# Used by RES_analyser.preprocess_text()

def _clean_text(df:DataFrame,text_cleaner:Callable[[str],str])->DataFrame:
      return (df
            .assign(text=lambda d: d.text.apply(text_cleaner))
            .assign(text_length=lambda d: [len(row.text) for row in d.itertuples()]))

# Upload text using supplied uploader function
# Used by RES_analyser.upload_text_to_s3()
      
def _upload_text(df:DataFrame,uploader:Callable,res_analyser)->DataFrame:
    upload = partial(uploader,aws_service=res_analyser.aws_service,config=res_analyser.config,logger=res_analyser.logger)
    return df.assign(uploaded=lambda d: [upload(str(row.Index),row.text) for row in d.itertuples()])

# Initiate comprehend analysis on S3 text documents

def _analyse_text(analyser:Callable,res_analyser)->dict:
    analyse = partial(analyser,
                      aws_service=res_analyser.aws_service,
                      config=res_analyser.config,
                      logger = res_analyser.logger)
    job_status = analyse()
    return job_status['EntitiesDetectionJobProperties']

# Add comprehend analysis results to dataframe
def _analysis_to_dataframe(df:DataFrame,results:list)->DataFrame:
    analysis = _extract_analysis(results=results)
    df['res_results']=Series(analysis)
    return df

# Offsets to dataframe
def _add_offsets(df:DataFrame,offset_cleaner,orphan_joiner)->DataFrame:
      return (df
            .assign(offsets=lambda d: d.res_results.apply(offset_cleaner))
            .assign(offsets_clean=lambda d: [orphan_joiner(row.text,row.offsets) for row in d.itertuples()]))

def _offset_cleaner(res_results):
    offsets = _collect_offsets(res_results)
    tuples = _offset_tuples(offsets)
    return _sorted_offsets(tuples)

def _orphan_joiner(text,offsets):
    otuples = _orphaned_I(text,offsets)
    offs =  _orphaned_word(text,otuples)
    return _regroup(offs)

def _collect_offsets(rrs):
    new_rrs = {}
    for rr in rrs:
        if rr['Score']>0.6:
            ent_type = rr['Type']
            if ent_type in ['VR','ER']:
                label = "NR"
            elif ent_type in ['EP','EV']:
                label = "EP"
            elif ent_type in ['CN','AF']:
                label = "AF"
            else:
                label = ent_type
            new_rrs.setdefault(label,[]).append((rr['BeginOffset'],rr['EndOffset']))
    return new_rrs



#####

def _add_res_sequence(df):
    temp_df = df.copy()
    temp_df['res_sequence'] = temp_df.offsets_clean.apply(_get_res_sequence)
    return temp_df
    
def _add_res_interactions(df):
    temp_df = df.copy()
    temp_df['res_interactions'] = temp_df.res_sequence.apply(_count_res_interactions)
    return temp_df

def _add_res_weights(df):
    temp_df = df.copy()
    temp_df['res_weights'] = temp_df.res_interactions.apply(_calc_res_weights)
    return temp_df

def _add_semantic_weights(df,ranking_factors={}):
    temp_df = df.copy()
    ranks = partial(_calc_semantic_weights,factors=ranking_factors)
    temp_df['semantic_weights'] = temp_df.res_weights.apply(ranks)
    return temp_df

def _add_res_adj_matrix(df):
    temp_df = df.copy()
    temp_df['res_adj_matrix'] = temp_df.semantic_weights.apply(_create_adj_matrix)
    return temp_df

def _get_res_sequence(offsets_clean):
    return [label for label in offsets_clean.values()]


def _empty_res_interactions() -> dict[tuple,int]:
    RE_types = ['RR','NR','AR','AF','EP']
    RE_interactions:dict[tuple,int] = dict()
    for t1 in RE_types:
        for t2 in RE_types:
            entry = tuple(sorted((t1,t2)))
            if entry not in RE_interactions.keys():
                RE_interactions[entry] = 0
    return RE_interactions

def _count_res_interactions(re_sequence:list[str]) -> dict[tuple,int]:
    re_ints = _empty_res_interactions()
    limit = len(re_sequence)-1
    for i,s in enumerate(re_sequence):
        if i < limit:
            rei = tuple(sorted((s,re_sequence[i+1])))
            #print(i,rei)
            re_ints[rei] += 1 
    return re_ints

def _calc_res_weights(interactions:dict[tuple,int])->dict[tuple,float]:
    max_count = max(interactions.values())
    if max_count == 0:
        max_count = 0.0001
    weights = dict()
    for edge,count in interactions.items():
        weights[edge] = round(count/(max_count),2)
    return weights



def _calc_semantic_weights(weights:dict[tuple,float], factors:dict[tuple,float]={})->dict[tuple,float]:
    if not factors:
        return weights
    else:
        for edge,w in weights.items():
            weights[edge] = factors[edge] * w
        return weights
        

def _create_adj_matrix(weights:dict[tuple,float])->list[list[float]]:
    re_types = ["RR","NR","AR","AF","EP"]
    matrix = []
    for r in re_types:
        row = []
        for c in re_types:
            key = tuple(sorted((r,c)))
            #print(key)
            weight = weights.get(key,0)
            row.append(weight)
        matrix.append(row)
    return matrix

### SIMILARITY ANALYSIS

def _jaccard_similarity(g1:Graph,g2:Graph)->float:
    return similarity(g1, g2, 
                      eweight1=g1.ep['e_weights'], eweight2=g2.ep['e_weights'], 
                      #label1=g1.vp['v_labels'], label2=g2.vp['v_labels'], 
                      norm=True, p=1.0, distance=False, asymmetric=False)
    
# def _cosine_similarity(m1,m2)->float:
#     v1 = list(chain.from_iterable(m1))
#     v2 = list(chain.from_iterable(m2))
#     return np.dot(v1,v2)/(norm(v1)*norm(v2))

def _vectorise_adj(matrix):
    return list(chain.from_iterable((matrix[i][j] for j in range(i,5)) for i in range(5)))
    
def zero_pos(am):
    nm = []
    for r,row in enumerate(am):
        nr = []
        for c,weight in enumerate(row):
            if r < 3 or c < 3:
                nr.append(weight)
            else:
                nr.append(0)
        nm.append(nr)
    return nm

def zero_mod(am):
    nm = []
    for r,row in enumerate(am):
        nr = []
        for c,weight in enumerate(row):
            if r >= 3 or c >= 3:
                nr.append(weight)
            else:
                nr.append(0)
        nm.append(nr)
    return nm

def _adj_vector(adj_matrix):
    return _vectorise_adj(adj_matrix)
    
def _positional_vector(adj_matrix):
    return _vectorise_adj(zero_pos(adj_matrix))
    
def _modal_vector(adj_matrix):
    return _vectorise_adj(zero_mod(adj_matrix))

def _cosine(A,B):
    return dot(A,B)/(norm(A)*norm(B))
        
def _am4idx(df,idx:int):
    return df.res_adj_matrix[idx]

def _similarity(m1,m2,vector_func):
    return float(_cosine(vector_func(m1),vector_func(m2)))

def _res_similarity(df,idx1,idx2,vector_func):
    return _similarity(_am4idx(df,idx1),_am4idx(df,idx2),vector_func)

_interaction_similarity = partial(_res_similarity,vector_func=_adj_vector)
_positional_similarity = partial(_res_similarity,vector_func=_positional_vector)
_modal_similarity = partial(_res_similarity,vector_func=_modal_vector)

def _similarities(df,idx1,idx2):
    return {"interaction": _interaction_similarity(df,idx1,idx2),
            "positional": _positional_similarity(df,idx1,idx2),
            "modal":_modal_similarity(df,idx1,idx2)}

    

### PIPELINE SUPPORT FUNCTIONS

# Clean return characters and strip whitespace
# Used by preprocess_text()
def _whitespace_cleaner(text:str)->str:
      return text.strip().replace('\r\n','\n')

# Upload text to S3
def _s3_text_uploader(idx:str,text:str,aws_service,config:dict,logger)->bool:
    try:
        response = aws_service.s3_client.put_object(Body=text,
                                        Bucket=aws_service.aws_params["s3_bucket_name"],
                                        Key=f"{config["s3_source_dir"]}/{idx}.txt")
    except Exception as e:
        logger.error("There was an error when uploading text to s3 %s",repr(e))
        return False
    else:
        if response['ResponseMetadata']['HTTPStatusCode']==200:
            logger.debug(f"File {idx} uploaded successfully")
            return True
        else:
            logger.error(f"File {idx} did not upload successfully to S3: {response}")
            return False
        
# Analyse text with comprehend custom entity recognizer
def _comprehend_cer_analyser(aws_service,config,logger)->dict:
    try:
        response = aws_service.comprehend_client.start_entities_detection_job(
            InputDataConfig={
                'S3Uri': _comprehend_input_uri(aws_service.aws_params["s3_bucket_name"],
                                               config["s3_source_dir"]),
                'InputFormat': 'ONE_DOC_PER_FILE'
            },
            OutputDataConfig={
                'S3Uri': _comprehend_output_uri(aws_service.aws_params["s3_bucket_name"],
                                                config["s3_target_dir"])
            },
            DataAccessRoleArn=_comprehend_access_role_arn(aws_service.aws_params["comprehend_service_role_name"],
                                                          aws_service.aws_account_number),
            JobName=f"res_analysis_{_date_string()}",
            EntityRecognizerArn=_comprehend_cer_arn(aws_service.aws_session.region_name,
                                                    aws_service.aws_account_number,
                                                    aws_service.aws_params["reflexive_entity_name"],
                                                    aws_service.aws_params["reflexive_entity_version"]),
            LanguageCode='en'
        )
    except Exception as e:
        logger.error("There was an error when analysing text with comprehend %s",repr(e))
        return {"ERROR":repr(e)}
    else:
        return aws_service.comprehend_client.describe_entities_detection_job(JobId=response['JobId'])

# Monitor a CER Analysis Job
def _cer_job_progress(status:dict,aws_service,tz,output)->dict:
    # Submitted
    job_name = status['JobName']
    job_id = status['JobId']
    submit_time = status['SubmitTime'].astimezone(ZoneInfo(tz))
    output(f"RES_ANALYSIS JOB {job_name} ({job_id}) submitted at: {submit_time}")
    
    # In progress
    while status['JobStatus'] in ["SUBMITTED","IN_PROGRESS"]:
        time = datetime.now().astimezone(ZoneInfo(tz))
        job_status = status['JobStatus']
        output(f"{time} [{job_id}] {job_name} status: {job_status}")
        sleep(10)
        properties = aws_service.comprehend_client.describe_entities_detection_job(JobId=job_id)
        status=properties['EntitiesDetectionJobProperties']
        
    # Finished (complete or error)
    job_status = status['JobStatus']
    end_time = status['EndTime'].astimezone(ZoneInfo(tz))
    time_taken = end_time - submit_time
    output_url = status['OutputDataConfig']['S3Uri']
    output(f"RES_ANALYSIS JOB {job_name} ({job_id}) finished with status: {job_status} at: {end_time}")
    output(f"Analysis time: {str(time_taken)}")
    output(f"Results available at: {output_url}")
    return status    
 
     
# Download from S3 to local
def _download_from_s3(res_analyser,status)->str:
    local_file_path = f"{res_analyser.config['local_data_dir']}/{status['JobName']}.tar.gz"
    bucket_name = res_analyser.aws_service.aws_params["s3_bucket_name"]
    try:
        output_key = status['OutputDataConfig']['S3Uri'].split(bucket_name)[1]
        with open(f"{local_file_path}",'wb') as output_data:
            res_analyser.aws_service.s3_client.download_fileobj(bucket_name,output_key[1:],output_data)  
    except Exception as e:
        res_analyser.logger.error("An error occured when downloading results from S3: %s",repr(e))
        local_file_path = None
    return local_file_path
   
# Extract results from tar.gz file and save as json  
def _extract_save_results(res_analyser,local_file_path)->list:
        # extract the tar archive
        files = list()
        with tarfile.open(f"{local_file_path}", "r:gz") as tf:
            for member in tf.getmembers():
                f = tf.extractfile(member)
                if f is not None:
                    content = f.read()
                    files.append(content)
        # extract results and save and return
        raw_results = files[0].decode("utf-8").split('\n')
        raw_results.pop() # pop last item off as empty entry due to final \n
        #
        #json_results = json.dumps(raw_results)
        #res_analyser.logger.info("raw_results>> ",raw_results)
        results = [json.loads(result) for result in raw_results]
        with open(f"{local_file_path[:-7]}.json","w") as fp:
            json.dump(results,fp)
        return results

# Get a dict of (index,entities) from cer analysis results
def _extract_analysis(results):
    file_ents =  ((result["File"],result["Entities"]) for result in results)
    idx_ents = ((int(file.split('_')[-1].split('.')[0]),ents) for file,ents in file_ents)
    return dict(idx_ents)


   
# Comprehend access role arn
def _comprehend_access_role_arn(comprehend_service_role_name,aws_account_number):
    return f"arn:aws:iam::{aws_account_number}:role/service-role/{comprehend_service_role_name}"

# Comprehend input url
def _comprehend_input_uri(s3_bucket_name,s3_files,prefix=""):
    return f"s3://{s3_bucket_name}/{s3_files}/{prefix}" 

# Comprehend output url
def _comprehend_output_uri(s3_bucket_name,s3_results):
    return f"s3://{s3_bucket_name}/{s3_results}/" 

# Comprehend entity recognizer arn
def _comprehend_cer_arn(region,account_number,cer_name,cer_version):
    return f"arn:aws:comprehend:{region}:{account_number}:entity-recognizer/{cer_name}/version/{cer_version}"
        
## Offset functions

def _offset_tuples(offsets):
    for k,vs in offsets.items():
        for b,e in vs:
            yield (b,(e,k))

def _sorted_offsets(offsets):
    return sorted(offsets)

def _orphaned_I(text,offsets):
    for b,(e,t) in offsets:
        if 'I' in text[(b-2):(b-1)].strip():
            #print(text[(b-2):e],t)
            yield (b-2, (e,t))
        else:
            yield (b, (e,t))
            
def _orphaned_word(text,offsets):
    coffs = {}
    p = (0,(-2,''))
    for b,(e,t) in offsets:
        #print(p[1][0])
        if (p[1][0]+3)>=b:
            #print("Prev:",p,f"|{df.text[0][p[0]:p[1][0]]}|")
            #print("<--->",f"|{df.text[0][(p[1][0]+1):(b-1)]}|")
            #print("This:",b,e,t,f"|{df.text[0][b:e]}|")
            #print()
            if len((text[p[0]:p[1][0]]).split(' '))<2:
                #print(f"Removing {p[0]},{p[1][0]},{p[1][1]}")
                coffs.pop(p[0])
                #print(f"Replacing {b},{e},{t} with {p[0]},{e},{t}")
                coffs[p[0]] = (e,t)
                p=(p[0],(e,t))
            else:
                coffs[b] = (e,t)
                p = (b,(e,t))
        else:
            coffs[b] = (e,t)
            p = (b,(e,t))
    return coffs.items()

def _regroup(offsets):
    grouped = (((b,e),k) for (b,(e,k)) in offsets)
    return dict(grouped)


   
   
### UTILITY FUNCTIONS  
   
# Create a reverse date string YYYYmmdd based on current local time   
def _date_string()->str:
    return datetime.today().strftime('%Y%m%d')

# Get the current local working dir
def _local_path(dir)->str:
    return os.getcwd()+dir

# Check if local directory exists
def _dir_exists_local(dir:str)->bool:
    return os.path.exists(_local_path(dir))

# Return function to create directory
def _create_dir(dir)->str:
    os.makedirs(_local_path(dir))
    return _local_path(dir)

# Create local directory if required
def _create_local_dir(dir,logger)->str:
    if not _dir_exists_local(dir):
        try:
            path = _create_dir(dir)
        except Exception as e:
            logger.error("There was an error creating the local directory: %s",repr(e))
        finally:
            return path
    else:
        return _local_path(dir)