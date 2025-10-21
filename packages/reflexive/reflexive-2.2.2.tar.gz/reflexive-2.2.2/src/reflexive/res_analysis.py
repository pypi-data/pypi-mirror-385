import logging
import os
from functools import (partial)
import pandas as pd
from reflexive.service import AWS_service
from reflexive.analysis_functions import (
    _clean_text,
    _whitespace_cleaner,
    _upload_text,
    _s3_text_uploader,
    _analyse_text,
    _comprehend_cer_analyser,
    _cer_job_progress,
    _download_from_s3,
    _extract_save_results,
    _analysis_to_dataframe,
    _add_offsets,
    _offset_cleaner,
    _orphan_joiner,
    _add_res_sequence,
    _add_res_interactions,
    _add_res_weights,
    _add_semantic_weights,
    _add_res_adj_matrix,
    _jaccard_similarity,
    _similarities,
    _date_string,
    _create_local_dir   
)
from reflexive.display_functions import (
    _create_displacy_ents,
    _render_annotated_text,
    _create_graph,
    _draw_graph
)

class RES_analyser:
    
    aws_service:AWS_service
    config:dict
    
    logger = logging.getLogger(__name__)
    
    ranking_factors = {('RR','RR'):0.5, ('NR','RR'):0.9, ('AR','RR'):0.9, ('AF','RR'):0.8, ('EP','RR'):0.7,  #Alpha sorted tuples
                        ('NR','NR'):0.6, ('AR','NR'):1.0, ('AF','NR'):0.8, ('EP','NR'):0.7, 
                        ('AR','AR'):0.6, ('AF','AR'):0.8, ('AR','EP'):0.7, 
                        ('AF','AF'):0.5, ('AF','EP'):0.6, 
                        ('EP','EP'):0.5}

    
    def __init__(self,parameters,prefix="res",postfix=None,dir="/data/")->None:
        
        self.config = self._build_config(prefix,postfix,dir)
        
        try:
            self.aws_service = AWS_service(parameters)
            self.aws_service.connect()
            self.aws_service.get_s3_client()
            self.aws_service.get_comprehend_client()
        except Exception as e:
            self.logger.error("There was an error setting up the AWS service: %s",repr(e))
        else:
            self.logger.info("AWS service setup successfully")
    
    ############################################################       
    # MAIN ANALYSIS METHODS
    
    # Import files for analysis
    def import_files_to_df(self,subdir="data_source/"):
        return pd.DataFrame.from_dict(self._open_files_in_subdir(subdir))
      
    # Preprocess the text
    # Uses clean_text() and whitespace_cleaner()
    # Accepts a df, Returns a df
    
    preprocess_text = partial(_clean_text,text_cleaner=_whitespace_cleaner)
    
    # Upload text to s3
    # Uses _upload_text()
    # Accepts a df with 'text' and returns a df with 'uploaded' column

    def upload_text_to_s3(self,df): 
        return _upload_text(df,uploader=_s3_text_uploader,res_analyser=self)
    
    # Initiate comprehend custom entity analysis
    # Uses _analyse_text()
    # Accepts a df with 'uploaded' and returns a df with 'analysed' column
    
    def analyse_text(self):
        return _analyse_text(analyser=_comprehend_cer_analyser,res_analyser=self)
    
    # Monitor analysis process
    def monitor_job_progress(self,status,tz="UTC",useprint=False):
        if useprint:
            output = print
        else:
            output = self.logger.info 
        return _cer_job_progress(status,self.aws_service,tz,output)
    
    # Download and extract results
    def results_download_save_extract(self,status):
        local_file = _download_from_s3(self,status)
        return _extract_save_results(self,local_file)
    
    # Add results to dataframe
    def add_res_results(self,df,results):
        return _analysis_to_dataframe(df,results)

    # Get offsets from results and add to dataframe
    process_offsets = partial(_add_offsets,offset_cleaner=_offset_cleaner,orphan_joiner=_orphan_joiner)
    
    # Add text_display_ents
    def add_text_display(self,df):
        df['text_display_ents'] = [_create_displacy_ents(r.doc_name,r.text,r.offsets_clean) for i,r in df.iterrows()]
        return df

    # Create adjacency matrix from offsets
    def add_interactions(self,df):
        #Get RE sequence
        df = _add_res_sequence(df)
        df = _add_res_interactions(df)
        df = _add_res_weights(df)
        df = _add_semantic_weights(df,self.ranking_factors)
        df = _add_res_adj_matrix(df)
        return df
    
    # def add_semantic_weights(self,df):
    #     return _add_semantic_weights(df,self.ranking_factors)

    # Graph Jaccard Similarity
    def get_jaccard_similarity(self,g1,g2):
        return _jaccard_similarity(g1,g2)
    
    def get_cosine_similarities(self,df,idx1,idx2):
        return _similarities(df,idx1,idx2)
    
    
    ############################################################
    # UTILITY METHODS
    
    # Create the config dict used by s3 and comprehend methods
    def _build_config(self,prefix:str,postfix:str,dir:str)->dict[str,str]:
        if not postfix:
            postfix = _date_string()
        return {"local_data_dir": _create_local_dir(dir,logger=self.logger),
                "s3_source_dir":f"{prefix}_files_{postfix}",
                "s3_target_dir":f"{prefix}_results_{postfix}"}
        
    # Import files
    def _open_files_in_subdir(self,subdir):
        file_path = os.path.join(os.getcwd(),subdir)
        file_names = []
        texts = []
        for file_name in sorted(os.listdir(file_path)):
            if not file_name.startswith('.'):
                file_names.append(file_name.split('.')[0])
                with open(os.path.join(file_path,file_name),'r') as fp:
                    texts.append(fp.read())
        return {"doc_name":file_names,"text":texts}
    
    
    
    
class RES_visualiser:
    
    config:dict
    
    logger = logging.getLogger(__name__)

    
    def __init__(self)->None:
        return None
        # self.config = self._build_config()
        
        # try:
            
        # except Exception as e:
        #     self.logger.error("There was an error setting up: %s",repr(e))
        # else:
        #     self.logger.info("setup successfully")
    
    ############################################################       
    # MAIN VISUALISATION METHODS
    
    def show_annotated_text(self,ents):
        return _render_annotated_text(ents)
    
    def save_annotated_text(self,name,ents,subdir="data/"):
        file_path = os.path.join(os.getcwd(),subdir)
        with open(f"{file_path}{name}.html","w") as fp:
            fp.write(_render_annotated_text(ents,inline=False))
    
    def create_res_graph(self,matrix=None,id=None):
        return _create_graph(matrix,id)
    
    def show_graph(self,graph):
        return _draw_graph(graph,True)
    
    def save_graph(self,graph):
        return _draw_graph(graph,False)
    
    ############################################################
    # UTILITY METHODS
    
    # def show_df_graphs(self,df,scale=10,inline=True) -> str:   
    #     for am in df.res_adj_matrix:
    #         if scale > 1:
    #             sm = self._scale_adj_matrix(am,scale)
    #         else:
    #             sm = am
    #         g = self.create_res_graph(sm)
    #         _draw_graph(g,True)
    #     return ""
    
    # def _scale_adj_matrix(self,adj_matrix,scale):
    #     new_adj = []
    #     for row in adj_matrix:
    #         new_row = []
    #         for c in row:
    #             new_row.append(round(c*scale,1))
    #         new_adj.append(new_row)
    #     return new_adj
    
    # Create the config dict used by s3 and comprehend methods
    # def _build_config()->dict[str,str]:
    #     return {"":"", 
    #             "":"",
    #             "":""}
        
        