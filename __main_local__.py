import sys
from src.main_entry import main_entry

if __name__ == "__main__":

    args = sys.argv[1:]
    if len(args) != 5:
        main_entry({})
    else:
        main_entry({'watson_api_key':args[0],'watson_skill_id':args[1],'watson_workspace_url':args[2],'bag_faq_url':args[3], 'vaccination_center_url':args[4]})

else:
    raise ImportError("Run this file directly, don't import it!")
