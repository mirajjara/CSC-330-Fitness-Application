#this script populates the db with the challenges
#to populate the database, run this script as a module using the command:
#python -m app.seed_data
#this creates the application instance, sets up the db, and seeds the challenges.

from app import create_app

app = create_app()

with app.app_context():
    from . import db
    from app.models import Challenge

    def seed_data():
        challenges = [
            {'name': 'Push Ups I', 'description': 'Get those arms ready for a superhero pose! Complete 10 push ups in one set', 'difficulty': 'Easy'},
            {'name': 'Push Ups II', 'description': 'Time to level up! Complete 20 push ups in two sets of 10 and show off those guns', 'difficulty': 'Medium'},
            {'name': 'Push Ups III', 'description': 'The ultimate push up challenge! Complete 30 push ups in three sets of 10 and earn your superhero cape', 'difficulty': 'Hard'},
            {'name': 'One Mile Run', 'description': 'Ready, set, go! Run one mile without stopping and feel the rush of endorphins', 'difficulty': 'Easy'},
            {'name': 'Two Mile Run', 'description': 'You\'ve got this! Run two miles without stopping and show off your endurance skills', 'difficulty': 'Medium'},
            {'name': 'Three Mile Run', 'description': 'The ultimate test of endurance! Run three miles without stopping and earn your marathon badge', 'difficulty': 'Hard'},
            {'name': 'Sit Ups I', 'description': 'Get ready to crunch! Complete 15 sit ups in one set and strengthen that core', 'difficulty': 'Easy'},
            {'name': 'Sit Ups II', 'description': 'Time to step it up! Complete 30 sit ups in two sets of 15 and show off your six pack', 'difficulty': 'Medium'},
            {'name': 'Sit Ups III', 'description': 'The ultimate core challenge! Complete 45 sit ups in three sets of 15 and earn your superhero abs', 'difficulty': 'Hard'},
            {'name': 'Cycling I', 'description': 'Pedal to the metal! Cycle for 10 minutes without stopping and feel the wind in your hair', 'difficulty': 'Easy'},
            {'name': 'Cycling II', 'description': 'You\'re on a roll! Cycle for 20 minutes without stopping and show off your cycling skills', 'difficulty': 'Medium'},
            {'name': 'Cycling III', 'description': 'The ultimate cycling challenge! Cycle for 30 minutes without stopping and earn your cycling badge', 'difficulty': 'Hard'},
        ]
        for challenge in challenges:
            db.session.add(Challenge(**challenge))
        db.session.commit()

    if __name__ == '__main__':
        seed_data()