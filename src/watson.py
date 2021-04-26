from ibm_watson import AssistantV1
from ibm_watson.assistant_v1 import DialogNodeOutputGenericDialogNodeOutputResponseTypeText, DialogNodeOutputTextValuesElement, DialogNodeOutput, CreateIntent, \
    DialogNode, Example
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class WatsonWrapper:
    workspace_id = ""

    def __init__(self, workspace_id, api_key, workspace_url):
        self.workspace_id = workspace_id
        self.assistant = AssistantV1(
            version='2020-04-01',
            authenticator=IAMAuthenticator(api_key)
        )
        self.assistant.set_service_url(workspace_url)

    def createIntent(self, uuid, question):
        response = self.assistant.create_intent(
            workspace_id=self.workspace_id,
            intent=uuid,
            description=question,
            examples=[
                {
                    'text': question,
                    'description': question
                }
            ]
        ).get_result()

    def createDialogNode(self, uuid, question, answer):
        dialogOutput = DialogNodeOutputGenericDialogNodeOutputResponseTypeText(
            response_type='text',
            values=[DialogNodeOutputTextValuesElement(text=answer)]
        )
        response = self.assistant.create_dialog_node(
            workspace_id=self.workspace_id,
            dialog_node=uuid,
            description=question,
            title=question,
            conditions='#' + uuid,
            output=DialogNodeOutput(generic=[dialogOutput])
        ).get_result()
