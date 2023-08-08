def calculate_daily_calorie_needs(input):
    """
    Calculate estimated daily calorie needs based on the Harris-Benedict equation.

    Args:
        gender (str): 'male' or 'female'.
        weight (float): Weight of the person.
        height (float): Height of the person.
        age (int): Age of the person in years.
        activity_level (str): Activity level ('sedentary', 'lightly active', 'moderately active', 'very active').
        unit_system (str, optional): Unit system for weight and height ('metric' or 'imperial'). Default is 'metric'.

    Returns:
        float: Estimated daily calorie needs.
    """
    # Conversion factors for unit system
    if input['unit_system'] == 'imperial':
        # Convert weight from pounds to kilograms (1 pound = 0.45359237 kilograms)
        weight_kg = input['weight'] * 0.45359237

        # Convert height from inches to meters (1 inch = 0.0254 meters)
        height_m = input['height'] * 0.0254
    else:
        weight_kg = input['weight']
        height_m = input['height']
    
    # Activity level multipliers
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'moderately active': 1.55,
        'very active': 1.725
    }

    # Calculate BMR (Basal Metabolic Rate) based on gender
    if input['gender'].lower() == 'male':
        bmr = 88.362 + (13.397 * weight_kg) + (4.799 * height_m) - (5.677 * input['age'])
    elif input['gender'].lower() == 'female':
        bmr = 447.593 + (9.247 * weight_kg) + (3.098 * height_m) - (4.330 * input['age'])
    else:
        raise ValueError("Invalid gender. Please use 'male' or 'female'.")

    # Calculate daily calorie needs by multiplying BMR with activity level multiplier
    daily_calories = bmr * activity_multipliers.get(input['activity_level'].lower(), 1.2)
    return daily_calories
