class GoalSettingService:
    @staticmethod
    def calculate_bmr(user):
        """
        Calculate Basal Metabolic Rate (BMR) based on a user's physical attributes.
        BMR is the number of calories needed for the body to perform basic life-sustaining functions.
        Uses the Mifflin-St Jeor Equation.

        Parameters:
        - user: User object containing height, weight, age, and gender attributes.

        Returns:
        - bmr: Calculated BMR in calories per day.
        """
        # Convert height from feet and inches to cm, and weight from lbs to kg
        height_cm = ((user.height_feet * 12) + user.height_inches) * 2.54
        weight_kg = user.weight_pounds / 2.20462
        
        # Calculate BMR using gender-specific formulas
        if user.gender == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * user.age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * user.age) - 161
        return bmr

    @staticmethod
    def calculate_daily_caloric_needs(user):
        """
        Calculate daily caloric needs based on user's activity level and BMR.
        Adjusts BMR based on user's activity level and goal.

        Parameters:
        - user: User object containing activity level and goal type attributes.

        Returns:
        - caloric_needs: Total daily caloric needs in calories.
        """
        # Define activity level multipliers
        activity_levels = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extra_active': 1.9
        }
        # Adjust BMR based on activity level
        caloric_needs = GoalSettingService.calculate_bmr(user) * activity_levels[user.activity_level]
        
        # Adjust caloric needs based on weight goal
        goal_adjustments = {
            'lose_weight': 0.9,
            'maintain_weight': 1.0,
            'gain_muscle': 1.1,
        }
        caloric_needs *= goal_adjustments[user.goal_type]

        return caloric_needs

    @staticmethod
    def suggest_macro_nutrient_targets(user):
        """
        Suggest macro nutrient targets based on user's caloric needs.
        Determines the distribution of proteins, carbohydrates, and fats.

        Parameters:
        - user: User object with goal type.

        Returns:
        - Dictionary of calculated macro nutrients in grams.
        """
        # Calculate daily caloric needs
        caloric_needs = GoalSettingService.calculate_daily_caloric_needs(user)

        # Define macro nutrient distribution ratios based on goal type
        macro_distribution = {
            'lose_weight': {'protein': 0.35, 'carbs': 0.35, 'fats': 0.3},
            'maintain_weight': {'protein': 0.3, 'carbs': 0.4, 'fats': 0.3},
            'gain_muscle': {'protein': 0.4, 'carbs': 0.3, 'fats': 0.3},
        }
        distribution = macro_distribution[user.goal_type]

        # Calculate macro nutrient amounts in grams
        protein_grams = (caloric_needs * distribution['protein']) / 4  # 4 calories per gram of protein
        carbs_grams = (caloric_needs * distribution['carbs']) / 4     # 4 calories per gram of carbs
        fats_grams = (caloric_needs * distribution['fats']) / 9       # 9 calories per gram of fats

        return {
            'calories': caloric_needs,
            'protein': protein_grams,
            'carbohydrates': carbs_grams,
            'fats': fats_grams
        }
