from flask import Flask,render_template,request,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import SelectField,SubmitField,StringField
from wtforms.validators import DataRequired
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine


app = Flask(__name__)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "mysql+mysqlconnector://root:@localhost/election_results"
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"
app.config['SECRET_KEY'] = 'any secret string'
db = SQLAlchemy(app)
Base = automap_base(db.Model)

engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
Base.prepare(engine, reflect=True)


States = Base.classes.states
Party = Base.classes.party
PollingUnit = Base.classes.polling_unit
Lga = Base.classes.lga
Ward = Base.classes.ward
AnnouncedPUResult = Base.classes.announced_pu_results
AnnouncedLgaResult = Base.classes.announced_lga_results



data= Lga.query.all()
class LGA(FlaskForm):
	name = SelectField(u"Select Local Government", choices=[x.lga_name for x in data])
	submit = SubmitField("Submit")


class PUnit(FlaskForm):
	name = StringField("Enter Polling unit id", validators=[DataRequired()])
	submit = SubmitField("Submit")



@app.route('/',methods=['GET', 'POST'])
@app.route('/index',methods=['GET', 'POST'])
def index():
    form= LGA()
    total_result=0
    submit_form=False


    if form.validate_on_submit():
        submit_form= True
        data=form.name.data
        lga = Lga.query.filter(Lga.lga_name == data).first()
        lga_polling_units = PollingUnit.query.filter(PollingUnit.lga_id == lga.lga_id).all()
        polling_ids = [x.uniqueid for x in lga_polling_units]
        results = AnnouncedPUResult.query.filter(
        AnnouncedPUResult.polling_unit_uniqueid.in_(polling_ids)
    ).all()
        total_result = sum([x.party_score for x in results])
        estimated_result = AnnouncedLgaResult.query.filter(AnnouncedLgaResult.lga_name == lga.lga_id
    ).first()
    # estimated_total = estimated_result.party_score
    return render_template("index.html",form=form,calculated_total=total_result,
    # estimated_total = estimated_total,
    submit_form=submit_form
    )





@app.route('/party')
def party():
    headings=["id","partyid","partyname"]
    party_data = Party.query.all()
    party=[(x.id,x.partyid,x.partyid) for x in party_data]    

    return render_template('party.html',headings=headings,party=party)





@app.route('/unit',methods=['GET', 'POST'])
def polling_unit():
    form = PUnit()
    headings=[]
    result=" "
    data=False
    
    
    if form.validate_on_submit():
        data=form.name.data
        polling_units = AnnouncedPUResult.query.filter(AnnouncedPUResult.polling_unit_uniqueid == data).all()
        result = [(str(x.date_entered),x.party_abbreviation,x.party_score) for x in polling_units  ]
        if len(result) > 0:
            data=True
            headings=["date","name","score"]  
    return render_template('pollingUnit.html',headings = headings,result=result,form=form,data=data)

 





















































if __name__=="__main__":
    app.run(debug=True)