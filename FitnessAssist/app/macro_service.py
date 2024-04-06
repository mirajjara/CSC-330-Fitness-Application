class GoalSettingService:
    @staticmethod
    def calculate_bmr(user):
        # Convert height from feet and inches to cm, and weight from lbs to kg
        height_cm = ((user.height_feet * 12) + user.height_inches) * 2.54
        weight_kg = user.weight_pounds / 2.20462
        
        if user.gender == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * user.age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * user.age) - 161
        return bmr

    @staticmethod
    def calculate_daily_caloric_needs(user):
        activity_levels = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        caloric_needs = GoalSettingService.calculate_bmr(user) * activity_levels[user.activity_level]
        
        goal_adjustments = {
            'lose_weight': 0.9,
            'maintain_weight': 1.0,
            'gain_muscle': 1.1,
        }
        caloric_needs *= goal_adjustments[user.goal_type]

        return caloric_needs

    @staticmethod
    def suggest_macro_nutrient_targets(user):
        caloric_needs = GoalSettingService.calculate_daily_caloric_needs(user)

        macro_distribution = {
            'lose_weight': {'protein': 0.35, 'carbs': 0.35, 'fats': 0.3},
            'maintain_weight': {'protein': 0.3, 'carbs': 0.4, 'fats': 0.3},
            'gain_muscle': {'protein': 0.4, 'carbs': 0.3, 'fats': 0.3},
        }
        distribution = macro_distribution[user.goal_type]

        protein_grams = (caloric_needs * distribution['protein']) / 4
        carbs_grams = (caloric_needs * distribution['carbs']) / 4
        fats_grams = (caloric_needs * distribution['fats']) / 9

        return {
            'calories': caloric_needs,
            'protein': protein_grams,
            'carbohydrates': carbs_grams,
            'fats': fats_grams
        }
