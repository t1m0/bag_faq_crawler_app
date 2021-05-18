import logging

from ibm_watson import AssistantV1, ApiException
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

    def get_intent(self, uuid):
        return self.assistant.get_intent(
            workspace_id=self.workspace_id,
            intent=uuid,
            export='true'
        ).get_result()

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

    def update_intent(self, intent):
        response = self.assistant.update_intent(
            workspace_id=self.workspace_id,
            intent=intent['intent'],
            new_description=intent['description'],
            new_examples=intent['examples']
        ).get_result()

    def delete_intent(self, uuid):
        response = self.assistant.delete_intent(
            workspace_id=self.workspace_id,
            intent=uuid
        ).get_result()

    def get_dialog_node(self, uuid):
        try:
            return self.assistant.get_dialog_node(
                workspace_id=self.workspace_id,
                dialog_node=uuid,
                export='true'
            ).get_result()
        except ApiException as e:
            logging.warning("Dialog node '"+uuid+"' not present!")
            return None

    def createDialogNode(self, uuid, question, answer, parent):
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
            output=DialogNodeOutput(generic=[dialogOutput]),
            parent=parent
        ).get_result()

    def update_dialog_node(self, uuid, question, answer, parent):
        dialog_output = DialogNodeOutputGenericDialogNodeOutputResponseTypeText(
            response_type='text',
            values=[DialogNodeOutputTextValuesElement(text=answer)]
        )
        response = self.assistant.update_dialog_node(
            workspace_id=self.workspace_id,
            dialog_node=uuid,
            new_description=question,
            new_title=question,
            new_output=DialogNodeOutput(generic=[dialog_output]),
            new_parent=parent
        ).get_result()

    def delete_dialog_node(self, uuid):
        response = self.assistant.delete_dialog_node(
            workspace_id=self.workspace_id,
            dialog_node=uuid
        ).get_result()

    def create_dialog_folder(self, uuid, title):
        self.assistant.create_dialog_node(
            workspace_id=self.workspace_id,
            dialog_node=uuid,
            title=title,
            type='folder'
        ).get_result()

    def list_dialog_nodes_for_parent(self, parent):
        dialog_nodes = {}
        response = self.assistant.list_dialog_nodes(
            workspace_id=self.workspace_id,
            page_limit=500
        ).get_result()
        for node in response['dialog_nodes']:
            if 'parent' in node and parent == node['parent']:
                current_node = {
                    'uuid': node['dialog_node'],
                    'question': node['title']
                }
                if 'output' in node.keys():
                    current_node['answer'] = node['output']['generic'][0]['values'][0]['text']
                dialog_nodes[node['dialog_node']] = current_node
        return dialog_nodes
