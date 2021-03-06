#!/usr/bin/env python
import datetime
import sys,json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from wellness.applogic.intermediary_module import Intermediary,Beneficiary,db
from collections import OrderedDict


class RetrieveIntermediary:
     def __init__(self,myjson):
          self.myjson=myjson

     def isAssignedBeneficiary(self):
          result={}
          try:
              
               intermediary_id=self.myjson["Username"]
                                  
          except Exception as e:
               #print "Content-type: text/html\n" 
               result["message"]="Error%s"%e.message
               return (json.JSONEncoder().encode(result))
          
          
          try:
               #engine=create_engine('mysql://root:ugnkat@localhost/wellness', echo=False) 
               engine=db
               # create a Session
               Session = sessionmaker(bind=engine)
               session = Session()
                                   
               # querying for a record in the physical_activity pattern table
               res= session.query(Intermediary,Beneficiary).filter(Intermediary.intermediary_id==Beneficiary.intermediary_id).filter(Beneficiary.intermediary_id==intermediary_id).first()
               if res is None:
                    result["message"]="This intermediary is not yet assigned a Beneficary."
               else: 
                    interm,ben=res
                    result["message"]="This intermediary is arleady assigned a Beneficary. Continuing with this intermediary will override details of an existing beneficiary"
                    result["Fname"]=ben.beneficiary_fname
                    result["Lname"]=ben.beneficiary_lname
                    result["Mobile"]=ben.beneficiary_mobile
                    result["Id"]=ben.id
               
               session.close()
               engine.dispose()
                    
               return (json.JSONEncoder().encode(result))                   
                                   
          except Exception as e:
               session.close()
               engine.dispose() 
                         
               #print "Content-type: text/html\n" 
                                   
               result["message"]="Error: %s"%e
               #print      
               return (json.JSONEncoder().encode(result))
               #sys.exit()
          
          
          
          
          
          
     def retrieveIntermediaryInDB(self):       
          result={}              
          
          counter=0
          intermediary_records={}          
          
          try:
               #engine=create_engine('mysql://root:ugnkat@localhost/wellness', echo=False) 
               engine=db
               # create a Session
               Session = sessionmaker(bind=engine)
               session = Session()

               data={}
               intermediaries_ids=[]
               # querying for intermediaries who have been assigned beneficiaries
               res= session.query(Intermediary,Beneficiary).filter(Intermediary.intermediary_id==Beneficiary.intermediary_id).all()
               
               for interm_tuple,ben_tuple in res:
                    if counter<10:
                         Key1="R0"
                    else:
                         Key1="R"
                    
                    data["D0"]="%s %s"%(interm_tuple.intermediary_fname,interm_tuple.intermediary_lname)      
                    data["D1"]="%s"%interm_tuple.intermediary_id   
                    data["D2"]="%s %s. Mobile:%s"%(ben_tuple.beneficiary_fname,ben_tuple.beneficiary_lname,ben_tuple.beneficiary_mobile)
                    
                    
                    intermediary_records["%s%s"%(Key1,counter)]=OrderedDict(sorted(data.items(), key=lambda t: t[0]))
                                       
                    intermediaries_ids.append(ben_tuple.intermediary_id)
                    counter=counter+1
                    
                    data={}
                    
                    
                    #res= session.query(Intermediary,Beneficiary).filter(Intermediary.intermediary_id not in Beneficiary.intermediary_id).all()
               res= session.query(Intermediary).all()
                    
                                        
               prevcounter=counter
               data={}
               found=0
               for interm_tuple in res:
                         
                    if counter<10:
                         Key1="R0"
                    else:
                         Key1="R"
                              
                    if prevcounter>=0:
                              
                         #for intermediary_id in intermediaries_ids:
                         #     print intermediary_id,interm_tuple.intermediary_id
                         #     if intermediary_id==interm_tuple.intermediary_id:
                         #          print "Break"
                         #          found=1
                         #          break;
                         #if found ==0:
                         if interm_tuple.intermediary_id not in intermediaries_ids:
                              data["D0"]="%s %s"%(interm_tuple.intermediary_fname,interm_tuple.intermediary_lname)      
                              data["D1"]="%s"%interm_tuple.intermediary_id   
                              data["D2"]="None"
                              intermediary_records["%s%s"%(Key1,counter)]=OrderedDict(sorted(data.items(), key=lambda t: t[0]))
                              
                              counter=counter+1
                                   
                         data={}
                         found=0
                                             
                    
                    
               session.close()
               engine.dispose()
               return(json.JSONEncoder().encode(OrderedDict(sorted(intermediary_records.items(), key=lambda t: t[0]))))
     
                                   
                                   
          except Exception as e:
                         
               #print "Content-type: text/html\n" 
               session.close()
               engine.dispose()
                                   
               intermediary_records["R00"]=e
               #print      
               return (json.JSONEncoder().encode(intermediary_records))
               #sys.exit()
                                         
     
     
#myjson={'Fname':'Lucas','Lname':'Katule','Username':'katulentwa@gmail.com'}
#obj=RetrieveIntermediary(myjson)
#result=obj.retrieveIntermediaryInDB()
#print result

#myjson={'Fname':'Lucas','Lname':'Katule','Username':'katulentwa@gmail.com'}
#obj=RetrieveIntermediary(myjson)
#result=obj.isAssignedBeneficiary()
#print result
