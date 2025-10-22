import os.path

from halerium_utilities.board import Board
from halerium_utilities.collab import CollabBoard
from halerium_utilities.file.card_ids import assign_new_card_ids_to_board
from halerium_utilities.hal_es.hal_e import HalE
from halerium_utilities.hal_es.hal_e_session import HalESession
from halerium_utilities.hal_es.schemas import SessionData
from halerium_utilities.utils.workspace_paths import (
    runner_path_to_workspace_path, workspace_path_to_runner_path)


class BoardPathSession(HalESession):
    """
    Class for Board Path Sessions.

    Board Path Session behave the same as HalE Sessions once instantiated,
    but are based on an already existing .board files instead of a Hal-E.
    """

    def __init__(self, board_path: str):
        """
        Initializes a new BoardPathSession instance.

        This constructor connects a session for a specific .board file and initializes
        a CollabBoard instance representing the board.

        Parameters
        ----------
        board_path : str
            The path of the .board file.
        """
        self.hale = None
        self.session_url = None

        self.board = CollabBoard(board_path)
        workspace_path = runner_path_to_workspace_path(board_path)

        self.session_data = SessionData.validate({"session_path": workspace_path})
        self._user_info = None

    def __repr__(self):

        return f"BoardPathSession(board_path='{self.board.file_path}')"

    @classmethod
    def from_hale_name(cls, hale_name: str, target_path: str) -> "BoardPathSession":
        """
        Instantiates a BoardPathSession based on a Hal-E name
        with the board file at a target_path instead of the
        path created by the Hal-E.

        Parameters
        ----------
        hale_name : str
            The name of the Hal-E on which to base the session.
        target_path : str
            The path where the Hal-E board file is placed.

        Returns
        -------
        BoardPathSession
        """
        template_path = HalE.from_name(hale_name).template_board
        template_path = workspace_path_to_runner_path(template_path)
        template_board = Board.from_json(template_path)

        # write instance file
        new_board = assign_new_card_ids_to_board(template_board, {}, inplace=True)
        new_board.to_json(target_path)

        return cls(board_path=target_path)
