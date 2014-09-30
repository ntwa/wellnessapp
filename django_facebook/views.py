from django.http import HttpResponse
from app.retrieve_meals_goal import RetrieveMealsGoal
from app.retrieve_activity_goal import RetrieveActivityGoal
from app.save_weight import SaveWeight
from app.save_meal import SaveMeal
from app.plot_activity_graph import PlotActivityGraph
from app.plot_weight_graph import PlotWeightGraph
from app.plot_meal_graph import PlotMealGraph
from app.retrieve_weight import RetrieveWeight
from app.sync_activity import SyncActivityModule
from app.save_points import SavePoints
from app.save_logs import SaveLogs
from app.authentication_module import Authentication
from app.retrieve_intermediary import RetrieveIntermediary
from app.save_meals_goal import SaveMealsGoal
from app.save_activity_goal import SaveActivityGoal
from app.save_comment import SaveComment
from app.retrieve_points import RetrievePoints
import os

from django.views.decorators.csrf import csrf_exempt
from collections import OrderedDict

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django_facebook import exceptions as facebook_exceptions, \
    settings as facebook_settings
from django_facebook.connect import CONNECT_ACTIONS, connect_user
from django_facebook.decorators import facebook_required_lazy
from django_facebook.utils import next_redirect, get_registration_backend, \
    to_bool, error_next_redirect, get_instance_for
from open_facebook import exceptions as open_facebook_exceptions
from open_facebook.utils import send_warning
import logging
import json,sys

#if there is an error then check if an object is imported above before being used

#view for facebook authentication

logger = logging.getLogger(__name__)

# Create your views here.
def retrieveMealGoal(beneficiary_id):
    obj=RetrieveMealsGoal(beneficiary_id)
    goal=obj.getGoal() #the returned goal is an encoded json object    
    return goal
def retrieveActivityGoal(beneficiary_id):
    obj=RetrieveActivityGoal(beneficiary_id)
    goal=obj.getGoal() #the returned goal is an encoded json object
    return goal

def plotActivityGraph(myjson,beneficiary_id):
    obj=PlotActivityGraph(myjson,beneficiary_id)
    datapoints=obj.getDataPoints() #the returned goal is an encoded json object
    return datapoints
    
def plotMealGraph(myjson,beneficiary_id):
    obj=PlotMealGraph(myjson,beneficiary_id)
    datapoints=obj.getDataPoints() #the returned goal is an encoded json object 
    return datapoints
    
def retrieveWeight(myjson,beneficiary_id):
    obj=RetrieveWeight(myjson,beneficiary_id)
    weight=obj.getWeight() #the returned goal is an encoded json object
    return weight

def plotWeightGraph(myjson,beneficiary_id):
    obj=PlotWeightGraph(myjson,beneficiary_id)
    datapoints=obj.getDataPoints() #the returned goal is an encoded json object 
    return datapoints

def retrieveScoreBoard(myjson,intermediary_id):
    obj=RetrievePoints(myjson,intermediary_id,1)
    status=obj.retrieveScoreGardensUrls()
    return status
def retrieveScoreGardens(myjson,intermediary_id):
    result={}
    obj=RetrievePoints(myjson,intermediary_id,1)
    status=obj.retrieveScoreGardensUrls()
    return status
    #result["message"]="Got here"
    #return HttpResponse(json.JSONEncoder().encode(result), mimetype='application/json')
    
def retrieveScoreTanks(myjson,intermediary_id):
    result={}
    obj=RetrievePoints(myjson,intermediary_id,1)
    status=obj.retrieveScoreGardensUrls()
    return status


def retriveAllData(beneficiary_id,intermediary_id):
    
    #capture activities on different days
    activity_tuples={"Today":{},"This week":{},"Last week":{},"This month":{},"Last month":{},"Last three months":{}}
    meals_tuples={"Today":{},"This week":{},"Last week":{},"This month":{},"Last month":{},"Last three months":{}}
    weight_tuples={"This month":{},"Last month":{},"Last three months":{}}
    score_tuples={"Today":{}}
    meals_goal_tuple={"Goal":{}} 
    activity_goal_tuple={"Goal":{}} 
    name_tuple={"Name":{}}
    
    for day,activity_tuple in activity_tuples.iteritems():
        myjson={"Day":day}
        new_tuple=plotActivityGraph(myjson,beneficiary_id)
        temp=json.loads(new_tuple)
        activity_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
    
        
    for day,meals_tuple in meals_tuples.iteritems():
        myjson={"Day":day}
        new_tuple=plotMealGraph(myjson,beneficiary_id)
        temp=json.loads(new_tuple)
        meals_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
        
    for day,weight_tuple in weight_tuples.iteritems():
        myjson={"Day":day}
        new_tuple=plotWeightGraph(myjson,beneficiary_id)
        temp=json.loads(new_tuple)
        weight_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))        
        
      
    for day,score_tuple in score_tuples.iteritems():
        myjson={"Day":day}
        new_tuple=retrieveScoreBoard(myjson,intermediary_id)
        temp=json.loads(new_tuple)
        score_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
        
        
    for goal,meals_goal in meals_goal_tuple.iteritems():
        new_tuple=retrieveMealGoal(beneficiary_id)
        temp=json.loads(new_tuple)
        meals_goal_tuple[goal]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
    
    for goal,activity_goal in activity_goal_tuple.iteritems():
        new_tuple=retrieveActivityGoal(beneficiary_id)
        temp=json.loads(new_tuple)
        activity_goal_tuple[goal]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
    
    alldata={}
    
    alldata["Activity"]=activity_tuples
    alldata["Meals"]=meals_tuples
    alldata["Weight"]=weight_tuples
    alldata["MealsGoal"]=meals_goal_tuple
    alldata["ActivityGoal"]=activity_goal_tuple
    alldata["ScoreBoard"]=score_tuples
    
    return(json.JSONEncoder().encode(OrderedDict(sorted(alldata.items(), key=lambda t: t[0]))))
    



@csrf_exempt
def dataloader(request,command_id):
    #myjsonpoints={"points":3}
    #myjsonclickscounter={"clickscounter":1}
    
     
    try:
        try:
            
            #intermediary_id=request.session['username']
            if request.user.is_authenticated():
                intermediary_id=request.user.email
            else:
                raise Exception("Access denied")
                
                
        except Exception as e:
            result={}
            result["R00"]={'F1':-6,'F0':e}# a code used when a beneficiary doesn't exist
            status=json.JSONEncoder().encode(result)
            status=json.JSONEncoder().encode(result)
            return HttpResponse(status, mimetype='application/json')
            
        
        #myjson=json.loads(request.body)
        myjson={'Username':intermediary_id}
        obj=RetrieveIntermediary(myjson)
        status=obj.isAssignedBeneficiary()
        status=json.loads(status)
        beneficiary_id=status["Id"]
        #return HttpResponse(status, mimetype='application/json') 
        
    except Exception as e: 
        beneficiary_id=None 
        #result={}
        activity_tuples={"Today":{},"This week":{},"Last week":{},"This month":{},"Last month":{},"Last three months":{}}
        meals_tuples={"Today":{},"This week":{},"Last week":{},"This month":{},"Last month":{},"Last three months":{}}
        weight_tuples={"This month":{},"Last month":{},"Last three months":{}}
        score_tuples={"Today":{},"This week":{},"Last week":{},"This month":{},"Last month":{},"Last three months":{}}
        meals_goal_tuple={"Goal":{}} 
        activity_goal_tuple={"Goal":{}} 

        for day,activity_tuple in activity_tuples.iteritems():
            result={}
            result["R00"]={'F1':-5,'F0':"You don't have a family member assigned to your account"}
            temp=result
            activity_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
        
            
        for day,meals_tuple in meals_tuples.iteritems():
            result={}
            myjson={"Day":day}
            result["P00"]={'D1':-5,'D0':"You don't have a family member assigned to your account"}
            temp=result
            meals_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
            
        for day,weight_tuple in weight_tuples.iteritems():
            result={}
            myjson={"Day":day}
            result["R00"]={'F1':-5,'F0':"You don't have a family member assigned to your account"}
            temp=result
            weight_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))        
            
          
        for day,score_tuple in score_tuples.iteritems():
            result={}
            myjson={"Day":day}
            result["R00"]={'D1':-5,'D0':"You don't have any beneficiary assigned to you. You can't be part of this game"}
            temp=result
            score_tuples[day]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
            
            
        for goal,meals_goal in meals_goal_tuple.iteritems():
            result={}
            result["Starch"]="None"
            result["Fruits"]="None"
            result["Fat"]="None"
            result["Protein"]="None"
            result["Dairy"]="None" 
            temp=result
            meals_goal_tuple[goal]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
        
        for goal,activity_goal in activity_goal_tuple.iteritems():
            result={}
            result["Goal"]={'Steps':-5}
            temp=result
            activity_goal_tuple[goal]=OrderedDict(sorted(temp.items(), key=lambda t: t[0]))
        
        alldata={}
        
        alldata["Activity"]=activity_tuples
        alldata["Meals"]=meals_tuples
        alldata["Weight"]=weight_tuples
        alldata["MealsGoal"]=meals_goal_tuple
        alldata["ActivityGoal"]=activity_goal_tuple
        alldata["ScoreBoard"]=score_tuples
        
        status=(json.JSONEncoder().encode(OrderedDict(sorted(alldata.items(), key=lambda t: t[0]))))

        return HttpResponse(status, mimetype='application/json')
    
    
    

    try:
        myjson=json.loads(request.body)
        obj=SavePoints(myjson,intermediary_id)
        status=obj.savePointsInDB()
        
        obj=SaveLogs(myjson,intermediary_id)
        status=obj.saveLogsInDB()
        #return HttpResponse(status, mimetype='application/json')
    except Exception as e:
        #errorcode={}
        #errorcode["error"]=e.message
        #status=json.JSONEncoder().encode(errorcode)
        #return HttpResponse(status, mimetype='application/json')
        pass
    
    if command_id =="RAD":
        alldata=retriveAllData(beneficiary_id,intermediary_id)
        return HttpResponse(alldata, mimetype='application/json')
    
    if command_id =="RMG":
        #RMG means retrieve meals goal
        goal=retrieveMealGoal(beneficiary_id)
        return HttpResponse(goal, mimetype='application/json')

    elif command_id =="RAG":
        #RAG means retrieve activity goal
        goal=retrieveActivityGoal(beneficiary_id)
        return HttpResponse(goal, mimetype='application/json') 
    
    elif command_id =="PAG":
        #PAG means plot activity graph
        myjson =json.loads(request.body)  
        datapoints=plotActivityGraph(myjson,beneficiary_id)
        return HttpResponse(datapoints, mimetype='application/json')
    
    elif command_id == "PMG":
        #PMG means plot meal graph or chart
        myjson =json.loads(request.body)  
        datapoints=plotMealGraph(myjson,beneficiary_id)
        return HttpResponse(datapoints, mimetype='application/json')        
    
    elif command_id =="RW":
        #RW means retrieve weight
        myjson =json.loads(request.body)  
        weight=retrieveWeight(myjson,beneficiary_id)
        return HttpResponse(weight, mimetype='application/json')
    
    elif command_id =="PWG":
        #WG means plot activity graph
        myjson =json.loads(request.body)  
        datapoints=plotWeightGraph(myjson,beneficiary_id)
        return HttpResponse(datapoints, mimetype='application/json')
    elif command_id=="RSB":
        #Retrieve score board
        #myjson={"Username":intermediary_id,"Day":"Last week"}
        myjson =json.loads(request.body) 
        status=retrieveScoreBoard(myjson,intermediary_id)
        return HttpResponse(status, mimetype='application/json')
    elif command_id=="RSG":
        #result={}
        #Retrieve score gardens
        #myjson={"Day":"Today"}

        #myjson =json.loads(request.body) 
        status=retrieveScoreGardens(myjson,intermediary_id)
        return HttpResponse(status, mimetype='application/json')
        #result["message"]="Got here%s"%intermediary_id
        #return HttpResponse(json.JSONEncoder().encode(result), mimetype='application/json')
    elif command_id=="RST":
        #result={}
        #Retrieve score gardens
        #myjson={"Day":"Today"}

        #myjson =json.loads(request.body) 
        status=retrieveScoreGardens(myjson,intermediary_id)
        return HttpResponse(status, mimetype='application/json')
        
        


def saveWeight(myjson,beneficiary_id):
    obj=SaveWeight(myjson,beneficiary_id)
    status=obj.saveWeightInDB() #the returned status is an encoded json object  
    return status 

def saveMeal(myjson,beneficiary_id):
    obj=SaveMeal(myjson,beneficiary_id)
    status=obj.saveMealInDB()#the returned status is an encoded json object  
    return status

def uploadActivity(myjson):
    obj=SyncActivityModule(myjson)
    status=obj.uploadActivity()
    return status

def saveComment(myjson,beneficiary_id):
    obj=SaveComment(myjson,beneficiary_id)
    status=obj.saveCommentInDB()
    return status

def saveActivityGoal(myjson,beneficiary_id):
    obj=SaveActivityGoal(myjson,beneficiary_id)
    status=obj.saveGoal()
    return status

def saveMealsGoal(myjson,beneficiary_id):
    obj=SaveMealsGoal(myjson,beneficiary_id)
    status=obj.saveGoal()
    return status

        
@csrf_exempt
def dataupdate(request,command_id):
      
    try:
             
        
        #myjson=json.loads(request.body)
        if request.user.is_authenticated():
            intermediary_id=request.user.email
        else:
            result={}
            result["R00"]={'F1':-6,'F0':"Access denied"}# a code used when an intermediary is not logged in
            status=json.JSONEncoder().encode(result)
            status=json.JSONEncoder().encode(result)
            if command_id =="SA":
                pass# This is an upload from a pedometer. 
            else:
                return HttpResponse(status, mimetype='application/json')   
         
        myjson={'Username':intermediary_id}
       
        obj=RetrieveIntermediary(myjson)
        status=obj.isAssignedBeneficiary()
        status=json.loads(status)
        beneficiary_id=status["Id"]
        #return HttpResponse(status, mimetype='application/json') 
        
    except Exception as e: 
        beneficiary_id=None 
        result={}
        message="iYou don't have a family member assigned to your account"
        #message=e.message
        result["R00"]={'F1':-5,'F0':message}# a code used when a beneficiary doesn't exist
        status=json.JSONEncoder().encode(result)
        status=json.JSONEncoder().encode(result)
        if command_id =="SA":
            pass# This is an upload from a pedometer.
        else:
            return HttpResponse(status, mimetype='application/json')
    
  
    try:
        myjson=json.loads(request.body)
        obj=SavePoints(myjson)
        status=obj.savePointsInDB()
        
        obj=SaveLogs(myjson)
        status=obj.saveLogsInDB()
        #return HttpResponse(status, mimetype='application/json')
    except Exception as e:
        #errorcode={}
        #errorcode["error"]=e.message
        #status=json.JSONEncoder().encode(errorcode)
        #return HttpResponse(status, mimetype='application/json')
        pass
    
          
    
    if command_id =="SW":
        #SW means retrieve save weight
        myjson =json.loads(request.body)
        status=saveWeight(myjson,beneficiary_id)
        return HttpResponse(status, mimetype='application/json')
    
    elif command_id == "SM":
        #result={}
        #SM means save meal
        myjson =json.loads(request.body)
        status=saveMeal(myjson,beneficiary_id) 
        return HttpResponse(status, mimetype='application/json') 

        #result["message"]="The food was recorded sucessfully"
        #return HttpResponse(json.JSONEncoder().encode(result), mimetype='application/json')
        
    elif command_id =="SA":
        
        myjson=json.loads(request.body)
        status=uploadActivity(myjson)
        return HttpResponse(status, content_type='application/json')
    
    elif command_id =="SC":
        
        myjson=json.loads(request.body)
        status=saveComment(myjson,beneficiary_id)
        return HttpResponse(status, content_type='application/json')
         
    
    elif command_id == "SAG":
        myjson=json.loads(request.body)
        status=saveActivityGoal(myjson,beneficiary_id)
        #errorcode={}
        #errorcode["message"]="gfgfgfg"
        #status=json.JSONEncoder().encode(errorcode)        
        return HttpResponse(status, content_type='application/json')
    
    elif command_id == "SMG":
        myjson=json.loads(request.body)
        status=saveMealsGoal(myjson,beneficiary_id)
        #errorcode={}
        #errorcode["message"]="gfgfgfg"
        #status=json.JSONEncoder().encode(errorcode)         
        return HttpResponse(status, content_type='application/json')      
    
        


@csrf_exempt
@facebook_required_lazy
def connect(request, graph):
    '''
    Exception and validation functionality around the _connect view
    Separated this out from _connect to preserve readability
    Don't bother reading this code, skip to _connect for the bit you're interested in :)
    '''
    backend = get_registration_backend()
    context = RequestContext(request)

    # validation to ensure the context processor is enabled
    if not context.get('FACEBOOK_APP_ID'):
        message = 'Please specify a Facebook app id and ensure the context processor is enabled'
        raise ValueError(message)

    try:
        response = _connect(request, graph)
    except open_facebook_exceptions.FacebookUnreachable, e:
        # often triggered when Facebook is slow
        warning_format = u'%s, often caused by Facebook slowdown, error %s'
        warn_message = warning_format % (type(e), e.message)
        send_warning(warn_message, e=e)
        additional_params = dict(fb_error_or_cancel=1)
        response = backend.post_error(request, additional_params)

    return response


def _connect(request, graph):
    '''
    Handles the view logic around connect user
    - (if authenticated) connect the user
    - login
    - register

    We are already covered by the facebook_required_lazy decorator
    So we know we either have a graph and permissions, or the user denied
    the oAuth dialog
    '''
    backend = get_registration_backend()
    context = RequestContext(request)
    connect_facebook = to_bool(request.REQUEST.get('connect_facebook'))

    logger.info('trying to connect using Facebook')
    if graph:
        logger.info('found a graph object')
        converter = get_instance_for('user_conversion', graph)
        authenticated = converter.is_authenticated()
        # Defensive programming :)
        if not authenticated:
            raise ValueError('didnt expect this flow')

        logger.info('Facebook is authenticated')
        facebook_data = converter.facebook_profile_data()
        # either, login register or connect the user
        try:
            action, user = connect_user(
                request, connect_facebook=connect_facebook)
            logger.info('Django facebook performed action: %s', action)
        except facebook_exceptions.IncompleteProfileError, e:
            # show them a registration form to add additional data
            warning_format = u'Incomplete profile data encountered with error %s'
            warn_message = warning_format % unicode(e)
            send_warning(warn_message, e=e,
                         facebook_data=facebook_data)

            context['facebook_mode'] = True
            context['form'] = e.form
            return render_to_response(
                facebook_settings.FACEBOOK_REGISTRATION_TEMPLATE,
                context_instance=context,
            )
        except facebook_exceptions.AlreadyConnectedError, e:
            user_ids = [u.get_user_id() for u in e.users]
            ids_string = ','.join(map(str, user_ids))
            additional_params = dict(already_connected=ids_string)
            return backend.post_error(request, additional_params)

        response = backend.post_connect(request, user, action)

        if action is CONNECT_ACTIONS.LOGIN:
            pass
        elif action is CONNECT_ACTIONS.CONNECT:
            # connect means an existing account was attached to facebook
            messages.info(request, _("You have connected your account "
                                     "to %s's facebook profile") % facebook_data['name'])
        elif action is CONNECT_ACTIONS.REGISTER:
            # hook for tying in specific post registration functionality
            response.set_cookie('fresh_registration', user.id)
    else:
        # the user denied the request
        additional_params = dict(fb_error_or_cancel='1')
        response = backend.post_error(request, additional_params)

    return response


def disconnect(request):
    context = RequestContext(request)
    
    '''
    Removes Facebook from the users profile
    And redirects to the specified next page
    '''
    if request.method == 'POST':
        messages.info(
            request, _("You have disconnected your Facebook profile."))
        profile = request.user.get_profile()
        profile.disconnect_facebook()
        profile.save()
    response = next_redirect(request)
    return response


def example(request):
    
    beneficiaries_counter=0
    context = RequestContext(request)
    try:
         
        if request.user.is_authenticated():#get the beneficiary name
            username=request.user.email
            myjson={'Username':username}
            obj=RetrieveIntermediary(myjson)
            status2=obj.isAssignedBeneficiary()
            status3=obj.countIntermediaries()
            status2=json.loads(status2)
            status3=json.loads(status3)
            beneficiary_fname=status2["Fname"]
            beneficiary_lname=status2["Lname"]
            beneficiary_ids=obj.retrieveIntermediaryInDB();
            beneficiary_ids=json.loads(beneficiary_ids)
            beneficiaries_counter=status3["counter"]
            
    except Exception:
        pass
   

    #context['authenticated']=status
    #context['username']=username
    if request.user.is_authenticated():
        context['fname']=beneficiary_fname
        context['lname']=beneficiary_lname
        ben_num={}
        key="R"
        for x in range(0,beneficiaries_counter):
            ben_num["R%s"%x]=x
        
        context['users_counter']=OrderedDict(sorted(ben_num.items(), key=lambda t: t[0]))
      
        myjson={"Day":"Today"}
         
        context["beneficiary_ids"]=beneficiary_ids
        intermediary_id=request.user.email
        obj=RetrievePoints(myjson,intermediary_id,1)
        result=obj.retrieveIndividualBadge()
               
        result=json.loads(result)

      
        context["badge"]=result["R00"]["D1"]
        context["sound"]=result["R00"]["D2"]     
        context.push()
        
    #return HttpResponse(template.render(context))
    
    return render_to_response('django_facebook/startapppage.htm', context)
    '''
    if request.user.is_authenticated():
        username=request.user.email
    else:
        username="Helo"
    context = RequestContext(request)
    myjson ={"Data":username}
    status=json.JSONEncoder().encode(myjson)
    return HttpResponse(status, content_type='application/json')
    '''
