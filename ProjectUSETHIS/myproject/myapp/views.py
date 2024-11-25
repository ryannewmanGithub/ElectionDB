from django.shortcuts import render
import sqlite3
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Index, DDL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func


class Base(DeclarativeBase):
    pass

class Candidate(Base):
    __tablename__ = "candidate"

   
    candidate_id = Column(Integer, primary_key = True)
    name = Column(String)
    party_name = Column(String)

    def getrowvalues(self):
        return [self.candidate_id, self.name, self.party_name]

    



class Election(Base):
    __tablename__ = "election"


    election_id = Column(Integer, primary_key=True)
    winner_name = Column(String)
    winner_id = Column(Integer)
    winner_votes = Column(Integer)

    def getrowvalues(self):
        return [self.election_id, self.winner_name, self.winner_id, self.winner_votes]

class Party(Base):
    __tablename__ = "party"

    party_id = Column(Integer, primary_key=True)
    party_name = Column(String)

    def getrowvalues(self):
        return [self.party_id, self.party_name]

engine = create_engine("sqlite:///testing.db", echo=True)
Base.metadata.create_all(engine)
rowtracker = []
coltracker = []

with Session(engine) as session:
    """
    cand1 = Candidate(
        candidate_id = 1,
        name = 'Mister M',
        party_name = 'Purple'
    )
    cand2 = Candidate(
        candidate_id = 2,
        name = 'Dave',
        party_name = 'Shield'
    )
    first = Election(
        election_id = 2024,
        winner_name = 'Mister M',
        winner_id = 1,
        winner_votes = 10_091_009
    )
    second = Election(
        election_id = 2028,
        winner_name = 'Dave',
        winner_id = 2,
        winner_votes = 900119
    )
    session.add_all([cand1, cand2, first, second])
    session.commit()
    """
    #p = Party(party_id = 1, party_name = "Purple")
    #s = Party(party_id = 2, party_name = "Shield")
    #session.add_all([p,s])
    #session.commit()
    #rows = session.execute(select(Election))
    rows = session.query(Election).all() # SELECT * FROM Election
    coltracker = Election.__table__.columns.keys()
    
    #print(coltracker)

    for row in rows:

        rowtracker.append(row.getrowvalues())
        
winnerIDX = DDL("CREATE INDEX winner_idx ON election (winner_id)")
#event.listen(Election.__table__, 'after_create', winnerIDX)
candidateIDX = DDL("CREATE INDEX candidate_idx on candidate (candidate_id)")


# Comment out because just need to run once. After that, will get error: index already exists
# These indexes benefit the JOIN ON election.winner_ID = candidate.candidate_id in the report feature.
# It also benefits all of the editing of candidates and elections, because to search for the row to edit, it does
# SELECT * FROM candidate WHERE candidate.candidate_ID = IDtoedit 
# SELECT * FROM election WHERE election.winner_ID = IDtoedit  (if a candidate name is modified in Election table, 
# look for other rows for that candidate)
# Also benefits deleting from candidate table because you check candidate ID in candidate and any matching winner ID in election
#with engine.connect() as conn:
    #conn.execute(winnerIDX)
    #conn.execute(candidateIDX)


# Create your views here.
def index(request):
    myinputs = []
    if request.method == "POST":
        breakflag = False
        #pass
        myinputs.append(request.POST.get("c1",""))
        if myinputs[0] == '':
            breakflag = True
            myinputs = []
        if not breakflag: # Adding a row to the Election table
            myinputs.append(request.POST.get("c2",""))

            myinputs.append(request.POST.get("c3",""))
            myinputs.append(request.POST.get("c4",""))


            
            with Session(engine) as session:
                newrow = Election(
                    election_id = int(myinputs[0]),
                    winner_name = myinputs[1],
                    winner_id = int(myinputs[2]),
                    winner_votes = int(myinputs[3])
                )
                

                # Makes sure that the Candidate exists before adding to election table
                q = session.query(Candidate).filter(Candidate.candidate_id == newrow.winner_id).first()
                if q:
                    if newrow.winner_name == q.name:
                        session.add_all([newrow])
                    
                else:
                    pass

                session.commit()
                #rowtracker.append(newrow.getrowvalues())
        
        exitfromdelete = False
        if breakflag:
            delID = (request.POST.get("deleteID",""))
            if delID == '':
                exitfromdelete = True
            if not exitfromdelete:
                delID = int(delID)
                #print("PRINTING DELID!!!!!!!!!")
                #print(delID)
                x = delID
                with Session(engine) as session:
                    deletedrow = session.query(Election).filter(Election.election_id == x).first()
                    #deletedcand = session.query(Candidate).filter(Candidate.candidate_id == deletedrow.winner_id).first()
                    if deletedrow:
                        print("DOING SESSION.DELETE!!!!!!!11")
                        session.delete(deletedrow)
                        #if deletedcand:
                         #   session.delete(deletedcand)
                        session.commit()
                    else:
                        pass

            if exitfromdelete:
                if request.POST.get("edit1","") != '':

                    edit1 = int(request.POST.get("edit1","")) # Edit candidates
                    edit2 = request.POST.get("edit2","")
                    edit3 = int(request.POST.get("edit3",""))
                    edit4 = int(request.POST.get("edit4",""))

                    with Session(engine) as session:
                        selectedrow = session.query(Election).filter(Election.election_id == edit1).first()
                        if selectedrow:
                            selectedrow.winner_name = edit2
                            #selectedrow.winner_id = edit3 DO NOT CHANGE ID
                            selectedrow.winner_votes = edit4

                            # If name is changed, also update other rows in Election table and Candidate table
                            otherrows = session.query(Election).filter(Election.winner_id == edit3).all()
                            for row in otherrows:
                                row.winner_name = edit2

                            thecand = session.query(Candidate).filter(Candidate.candidate_id == edit3).first()
                            if thecand:
                                thecand.name = edit2

                            session.commit()
                        else:
                            pass
            
            addID = request.POST.get("addc1","")
            if addID != '':
                addname = request.POST.get("addc2","") # Add to Candidate table
                addparty = request.POST.get("addc3","")
                
                with Session(engine) as session:
                    # Makes sure that Party for new candidate is already existing (enforce foreign key constraint)
                    checker = session.query(Party).filter(Party.party_name == addparty).first()
                    if checker:
                        toadd = Candidate(candidate_id=int(addID), name=addname, party_name=addparty)
                        session.add_all([toadd])
                        session.commit()
            
            delcand = request.POST.get("deleteIDCand","")
            if delcand != '':
                with Session(engine) as session:
                    # Deleting a candidate
                    todelete = session.query(Candidate).filter(Candidate.candidate_id == int(delcand)).first()

                    anywinners = session.query(Election).filter(Election.winner_id == int(delcand)).all()
                    if todelete:
                        session.delete(todelete)

                        if anywinners: # Also delete corresponding entries in Election table
                            for row in anywinners:
                                session.delete(row)
                        session.commit()
            editcand = request.POST.get("candedit1", "")
            if editcand != '':
                with Session(engine) as session:
                    editedcand = session.query(Candidate).filter(Candidate.candidate_id == int(editcand)).first()
                    # This gets the row to edit in the Candidate table and also find any corresponding elections
                    affectedelection = session.query(Election).filter(Election.winner_id == int(editcand)).all()

                    if editedcand:
                        newname = request.POST.get("candedit2","")
                        newparty = request.POST.get("candedit3","")
                        
                        partycheck = session.query(Party).filter(Party.party_name == newparty).first()
                        # After editing, the Party of a candidate must be an existing party
                        if partycheck:
                            # This performs the edits
                            editedcand.name = newname
                            editedcand.party_name = newparty

                            if affectedelection:
                                for row in affectedelection:
                                    row.winner_name = newname
                            session.commit()

            addingparty = request.POST.get("partyc1","")
            if addingparty != '':
                with Session(engine) as session:
                    pname = request.POST.get("partyc2","")
                    checkexisting = session.query(Party).filter(Party.party_name == pname).first()
                    # Check to see if there are parties with same name
                    # This enforces the constraint that party names must be unique
                    # Users can only add parties with different names from existing parties
                    if not checkexisting:
                        p = Party(party_id = int(addingparty), party_name = pname)
                        session.add_all([p])
                        session.commit()

            deletingparty = request.POST.get("deleteIDParty","")
            if deletingparty != '':
                
                with Session(engine) as session:
                    deletethisrow = session.query(Party).filter(Party.party_id == int(deletingparty)).first()

                    changed_cands = session.query(Candidate).filter(Candidate.party_name == deletethisrow.party_name).all()
                    for row in changed_cands:
                        row.party_name = 'Unknown'
                        # If a party is deleted, don't delete corresponding Candidate. Instead, change
                        # the candidate's party to 'Unknown'

                    if deletethisrow:
                        # Enforce constaint that Unknown is a special value that cannot be deleted
                        if deletethisrow.party_name != 'Unknown': 
                        
                            session.delete(deletethisrow)
                            session.commit()

            editparty = request.POST.get("editIDParty","")
            if editparty != '':
                with Session(engine) as session:
                    editpartyrow = session.query(Party).filter(Party.party_id == int(editparty)).first()
                    # Find corresponding candidate rows
                    candrows = session.query(Candidate).filter(Candidate.party_name == editpartyrow.party_name).all()
                    if editpartyrow:
                        newpartyname = request.POST.get("editIDParty2","")
                        if editpartyrow.party_name != 'Unknown': # Unknown is a special value, cannot be edited
                            editpartyrow.party_name = newpartyname

                            if candrows:
                                for row in candrows:
                                    # Editing a party name will change the party name for 
                                    # all corresponding candidates.
                                    row.party_name = newpartyname

                            session.commit()

                        

    mydict = {'inputs':myinputs}
    
    rowtracker = []
    candrowtracker = []
    partyrowtracker = []

    # This gets all the rows and column names for all 3 tables
    with Session(engine) as session:
        rows = session.query(Election).all()
        for row in rows:
            rowtracker.append(row.getrowvalues())
        coltracker = Election.__table__.columns.keys()

        rows = session.query(Candidate).all()
        for row in rows:
            candrowtracker.append(row.getrowvalues())
        candcoltracker = Candidate.__table__.columns.keys()

        partycoltracker = Party.__table__.columns.keys()
        rows = session.query(Party).all()
        for row in rows:
            partyrowtracker.append(row.getrowvalues())
        



    mydict['rowtracker'] = rowtracker
    mydict['candrowtracker'] = candrowtracker
    mydict['partyrowtracker'] = partyrowtracker

    mydict['coltracker'] = coltracker
    mydict['candcoltracker'] = candcoltracker
    mydict['partycoltracker'] = partycoltracker
    # Passes the row and column information to the html
    return render(request, "index.html", mydict)

def report(request):
    mydict = {}
    plist = []
    clist = []
    with Session(engine) as session:
            
        parties = session.query(Party).all()
        cands = session.query(Candidate).all()
        for party in parties:
            plist.append(party.party_name)
        for c in cands:
            clist.append(c.name)
    mydict['plist'] = plist
    mydict['clist'] = clist

    joinedrows = []

    if request.method == 'POST':
        selectedparties = request.POST.getlist("firstlist[]")
        selectedcands = request.POST.getlist("secondlist[]")
        #print(vals) #It prints what is in the value= part of the html
        #print(selectedparties)
        #print(selectedcands)
        with Session(engine) as session:
            #joinquery = session.query(Election).join(Candidate).all()#.filter(Election.winner_id == Candidate.candidate_id).all()

            candcoltracker = Candidate.__table__.columns.keys()
            electcoltracker = Election.__table__.columns.keys()

            colList =  electcoltracker + candcoltracker
            mydict['colList'] = colList

            # For computing the average
            totalcount = session.query(func.count()).select_from(Election).scalar()

            if len(selectedparties) > 0 and len(selectedcands) > 0:
                # Check if in selected candidates and selected parties in all 3 queries ---------------------------------->
                joinquery = session.query(Election, Candidate).join(Election, Election.winner_id == Candidate.candidate_id).filter(Election.winner_name.in_(selectedcands)).filter(Candidate.party_name.in_(selectedparties)).all()
                countquery = session.query(func.count().label('Win Count')).select_from(Election,Candidate).join(Election,Election.winner_id == Candidate.candidate_id).filter(Election.winner_name.in_(selectedcands)).filter(Candidate.party_name.in_(selectedparties))
                avgquery = session.query(func.avg(Election.winner_votes).label('Average Votes')).select_from(Election,Candidate).join(Election,Election.winner_id == Candidate.candidate_id).filter(Election.winner_name.in_(selectedcands)).filter(Candidate.party_name.in_(selectedparties))

            elif len(selectedparties) == 0:
                # Check if in selected candidates in all 3 queries ---------------------------------->
                joinquery = session.query(Election, Candidate).join(Election, Election.winner_id == Candidate.candidate_id).filter(Election.winner_name.in_(selectedcands)).all()
                countquery = session.query(func.count().label('Win Count')).select_from(Election,Candidate).join(Election,Election.winner_id == Candidate.candidate_id).filter(Election.winner_name.in_(selectedcands))
                avgquery = session.query(func.avg(Election.winner_votes).label('Average Votes')).select_from(Election,Candidate).join(Election,Election.winner_id == Candidate.candidate_id).filter(Election.winner_name.in_(selectedcands))

            elif len(selectedcands) == 0:
                # Check if in selected parties in all 3 queries ---------------------------------->
                joinquery = session.query(Election, Candidate).join(Election, Election.winner_id == Candidate.candidate_id).filter(Candidate.party_name.in_(selectedparties)).all()
                countquery = session.query(func.count().label('Win Count')).select_from(Election,Candidate).join(Election,Election.winner_id == Candidate.candidate_id).filter(Candidate.party_name.in_(selectedparties))
                avgquery = session.query(func.avg(Election.winner_votes).label('Average Votes')).select_from(Election,Candidate).join(Election,Election.winner_id == Candidate.candidate_id).filter(Candidate.party_name.in_(selectedparties))

            #print("Countquery is: !!!!!!!!!!!!!!!!!!!!")
            print("LOOK HERE FOR COUNTQUERY VALUE!!!!!!!!", countquery.first())
            for electionrow, candidaterow in joinquery:
                joinedrows.append(electionrow.getrowvalues() + candidaterow.getrowvalues())

            mydict['joinedrows'] = joinedrows
            mydict['thecount'] = str(countquery.scalar())
            mydict['theavg'] = str(avgquery.scalar())
            mydict['countcol'] = countquery.column_descriptions[0]['name']
            mydict['avgcol'] = avgquery.column_descriptions[0]['name']
            mydict['ratio'] = countquery.scalar() / totalcount
            mydict['selectedparties'] = selectedparties
            mydict['selectedcands'] = selectedcands
                
            mydict['displaystatistics'] = True


            
            
        

    
    return render(request, "report.html", mydict)