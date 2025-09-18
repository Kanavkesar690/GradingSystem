from flask import Flask, jsonify,request
from AutomatedSurveyFeedbackAnalysis.AutomatedSurveyFeedbackAnalysis import Automated_Survey_Feedback_Analysis
from AutomatedGradingFeedback.AutomatedGradingFeedback import Automated_Grading_Feedback


app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Hello from Flask"})

# Automated Survey & Feedback Analysis Task
@app.route("/AutomatedSurveyFeedbackAnalysis", methods=["GET"])
def analysis():
    task = request.args.get('task')
    return Automated_Survey_Feedback_Analysis(task)


@app.route("/AutomatedGradingFeedback", methods=["GET"])
def grading_feedback():

    StudyFiles, AssignmentFiles = request.args.get('StudyFiles'), request.args.get('AssignmentFiles')
    return Automated_Grading_Feedback(StudyFiles, AssignmentFiles)

app.run()