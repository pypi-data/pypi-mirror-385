"""
This module allows the creation of different interactive menus

Example:
    Shortest way to print the interactive menu in the terminal.
    For the three int entered as args
    (3, 4, 5) (Option per Column, Options Rows, Number char per option).

    >>> test_menu = Menu("test_menu", 3, 4, 5,
    ...                  [
    ...                      "test", "....", "menu",
    ...                      "test", "....", "menu",
    ...                      "test", "....", "menu",
    ...                      "test", "....", "menu",
    ...                  ])
    >>> test_menu.show_frame_menu()
    +-------------------------+
    |        test_menu        |
    |-------------------------|
    |                         |
    | > test    ....    menu  |
    |                         |
    |   test    ....    menu  |
    |                         |
    |   test    ....    menu  |
    |                         |
    |   test    ....    menu  |
    +-------------------------+
"""

from math import ceil
from collections.abc import Callable

__version__ = "1.0.0"

DEFAULT_CHARACTERS = {
    "cursor_values": ("   ", " > "),
    "BodyEmptyRow": " ",
    "RowLimit": "|",
    "MenuLimitRowBody": "-",
    "MenuCorner": "+",
    "CharacterOverflow": "...",
    "SpaceCharacter": " ",
    "ScrollBarValues": ("\x1b[48;5;0m \x1b[0m", "\x1b[48;5;255m \x1b[0m")
}


# HotKeys
OK_BUTTON = "Q"
MOVE_UP = "W"
MOVE_DOWN = "S"
MOVE_LEFT = "A"
MOVE_RIGHT = "D"



class Menu:
    """
    Class that provides methods for creating and interacting with the menu.
    """


    def __init__(self, title_menu: str, option_per_column: int,
                 rows_per_page: int, character_per_option: int,
                 options_list: list[str], dynamic_static_menu: bool = True):

        # Set default character
        self._cursor = DEFAULT_CHARACTERS["cursor_values"]
        self._scrollbar = DEFAULT_CHARACTERS["ScrollBarValues"]
        self._body_empty_row = DEFAULT_CHARACTERS["BodyEmptyRow"]
        self._row_limit = DEFAULT_CHARACTERS["RowLimit"]
        self._menu_limit_body = DEFAULT_CHARACTERS["MenuLimitRowBody"]
        self._menu_corner = DEFAULT_CHARACTERS["MenuCorner"]
        self._character_overflow = DEFAULT_CHARACTERS["CharacterOverflow"]
        self._space_character = DEFAULT_CHARACTERS["SpaceCharacter"]

        # Menu structure
        self._option_per_column = option_per_column
        self._options_rows_per_page = rows_per_page
        self._total_rows_body_menu = rows_per_page * 2 + 1
        self._character_per_option = character_per_option
        self._number_pages = ceil(
            (len(options_list) / (option_per_column * rows_per_page))
        )
        self._max_index = option_per_column * rows_per_page * self._number_pages
        self._characters_per_row = (
                len(self._cursor[False]) * option_per_column
                + character_per_option * option_per_column
                # Spaces char before Scroll-Bar
                + 2
                # Width to Scroll-Bar
                + 1
        )
        self._option_cutoff_point = (
                character_per_option - len(self._character_overflow)
        )

        # Menu main features
        self._type_menu = dynamic_static_menu
        self.activated: bool = True
        self._title_menu = self._fit_word_width(
            title_menu,
            self._characters_per_row,
            self._character_overflow,
            ""
        )
        self._cursor_coordinates: tuple[int, int, int] = (0, 0, 0)

        # Set default menu rows
        self._title_row = (self._row_limit
                           + self._title_menu.center(self._characters_per_row)
                           + self._row_limit)
        self._separate_row = (self._row_limit
                              + self._menu_limit_body * self._characters_per_row
                              + self._row_limit)
        self._limit_menu = (self._menu_corner
                            + self._menu_limit_body * self._characters_per_row
                            + self._menu_corner)
        self._empty_row = [
            self._row_limit,
            self._body_empty_row * (self._characters_per_row - 1),
            self._scrollbar[False],
            self._row_limit
        ]

        # Check input parameters
        if not options_list:
            raise ValueError(
                "The param options_list cannot be empty list")
        if self._option_per_column <= 0:
            raise ValueError(
                "The param option_per_column must be greater than 0")
        if self._options_rows_per_page <= 0:
            raise ValueError(
                "The param rows_per_page must be greater than 0")
        if self._character_per_option <= len(self._character_overflow):
            raise ValueError(
                "The param character_per_option must be greater than {}"
                .format(len(self._character_overflow)))
        # Minimum number of rows so that the scroll bar has enough space
        if self._total_rows_body_menu < self._number_pages:
            raise ValueError(
                "The param rows_per_page must be greater than {} with option_per_column value ({})"
                .format(ceil(self._max_index
                             / (self._option_per_column * 4)
                             - 1),
                        self._option_per_column)
            )

        # Generate menu
        self._options_list = self._options_list_processing(options_list)

        # noinspection PyTypeChecker
        self.__setitem__((*self._cursor_coordinates, 0), self._cursor[True])
        self._set_scroll_bar()

        # Relates menu coordinates to the name of the options for then enter functions.
        self._functions_dictionary = self._create_functions_dictionary(options_list)


    def __setitem__(self, key: tuple[int, int, int, int] | tuple[int, int, int], value: str):
        """Changes values into the rows that you want"""
        size_item = len(key)

        # Page value
        page = key[0] + 3

        # Changes cursor or option values
        # Get Option (if item[3] == 1) or cursor (if item[3] == 0) value
        if size_item == 4:
            # Check if the indexes values into the limits
            self._indexes_error(key)

            row = key[1] * 2 + 1
            col = key[2] + 1
            cursor_or_option = key[3]
            self._options_list[page][row][col][cursor_or_option] = value

        # Changes Scroll-Bar, LimitRows, Others values in specific row
        elif size_item == 3:
            # Check if the indexes values into the limits
            self._indexes_error(key)

            row = key[1]
            col = len(self._options_list[page][row]) - 2
            self._options_list[page][row][col] = value

        else:
            raise ValueError("Iterable size 3 - 4: {};\n Param key = {}".format(size_item, key))


    def __getitem__(self, item: tuple[int, int, int, int] | tuple[int, int, int]):
        """Return value into the rows that you want"""

        size_item = len(item)

        # Get Option (if item[3] == 1) or cursor (if item[3] == 0) value
        if size_item == 4:
            # Check if the indexes values into the limits
            self._indexes_error(item)

            page = item[0] + 3
            row = item[1] * 2 + 1
            col = item[2] + 1
            cursor_stroption = item[3]
            return self._options_list[page][row][col][cursor_stroption]

        elif size_item == 3:
            # Check if the indexes values into the limits
            self._indexes_error(item)

            page = item[0] + 3
            row = item[1]
            col = len(self._options_list[page][row]) - 2
            return self._options_list[page][row][col]

        else:
            raise ValueError("Iterable size 3 - 4")


    def _set_scroll_bar(self):
        # Set Scroll-Bar each pages values
        rows_group = int(self._total_rows_body_menu
                         / self._number_pages)
        module = self._total_rows_body_menu % self._number_pages

        # Obtain the size of the rows groups by adding the surplus
        n_rows_groups = [rows_group + 1 if page < module else rows_group
                         for page in range(self._number_pages)]

        # Rows per page where the Scroll-Bar is activating
        scrollbar_groups = []
        for i, n_rows in enumerate(n_rows_groups):
            scrollbar_groups.append(tuple(
                # The range of rows that the scroll-bar will be active
                range(
                    sum(n_rows_groups[: i]), sum(n_rows_groups[: i + 1])
                )
            ))

        # Activating Scroll-Bar as appropriate page
        for page, sb_active in enumerate(scrollbar_groups):
            for row in sb_active:
                scroll_bar = self._scrollbar[True]
                self.__setitem__((page, row, 0), scroll_bar)


    def _options_list_processing(self, input_options_list: list[str]):
        """
        Process the ``input_options_list``, so that useful in class

        This adds empty options to the input list for complete the menu,
        adjusts the char width of the options
        and changes the indexing of the list to fit the coordinate system this class.
        """

        def same_len_list_elements(input_list: list[str]):
            """Fill the entire menu with options and adjust width them."""

            adjusted_elements = input_list + [""] * (self._max_index - list_size)
            adjusted_elements = list(
                map(
                    lambda option: self._fit_word_width(option,
                                                        self._character_per_option,
                                                        self._character_overflow,
                                                        self._space_character),
                    adjusted_elements
                )
            )
            return adjusted_elements


        def add_cursor_to_option(input_list: list[str]):
            """Create columns; Add cursor to options"""

            cursor = self._cursor[False]
            options_with_cursor: list[list[str] | str] = list(
                map(lambda opt: [cursor, opt], input_list)
            )
            return options_with_cursor


        def create_body_rows(input_list: list[str]):
            rows_list: list[list[str] | str] = []

            for ii in range(0, len(input_list), self._option_per_column):
                # Add Row Options
                row = input_list[ii: ii + self._option_per_column] + ["  "]
                # Add BorderRow
                row.insert(0, self._row_limit)
                # Add ScrollBar
                row.append(self._scrollbar[False])
                # Add BorderRow
                row.append(self._row_limit)
                # Add Row to list
                rows_list.append(row.copy())

            return rows_list


        def create_body_page(input_list: list[list[str] | str]):
            pages_list = []
            for i in range(0, len(input_list), self._options_rows_per_page):
                page = []
                options_row = input_list[i: i + self._options_rows_per_page]
                [page.extend((self._empty_row.copy(), options_row)) for options_row in options_row]
                page.append(self._empty_row.copy())

                pages_list.append(page)

            return pages_list

        # Create title
        title_menu = [self._limit_menu, self._title_row, self._separate_row]


        # Create body Menu
        list_size = len(input_options_list)

        # Fill the entire menu with options and adjust width them.
        body_menu = same_len_list_elements(input_options_list)

        # Create columns; Add cursor to options
        body_menu = add_cursor_to_option(body_menu)


        # Structural change of list to approach the coord system.
        body_menu = create_body_rows(body_menu)


        # Create Pages
        body_menu = create_body_page(body_menu)


        return title_menu + body_menu + [self._limit_menu]


    def _create_functions_dictionary(self, input_options_list: list[str]):
        functions_dictionary = {}
        page = 0
        row = 0
        col = 0

        for i, option in enumerate(input_options_list):
            # Add the option to the dictionary and its coordinate as a key
            functions_dictionary.update({(page, row, col): option})

            # Adjusts the indexes for menu coord system
            col += 1
            if col >= self._option_per_column:
                col = 0
                row += 1

            if row >= self._options_rows_per_page:
                row = 0
                page += 1

        return functions_dictionary


    def add_function_to_menu(self, functions_and_kwargs: list[tuple[Callable, dict]] | tuple[tuple[int, int, int], Callable, dict]):
        """
        To call a function you want when **OK_BUTTON** is pressed

        To fill all the options with functions, use the list structure: 'list[tuple[Callable, dict]]';
        Where each option corresponds to a tuples into the list. The first tuple element represents
        the `Function`, the second the `**kwargs` corresponding to it.

        To selectively fill only some of the options with functions,
        use the tuple structure: tuple[tuple[int, int, int], Callable, dict]';
        Where the first element represents the `option's coord`, the second
        the `Function`, and the third the `**kwargs` corresponding to it.

        """

        # This is to insert functions on all the options.
        if type(functions_and_kwargs) == list:
            # Checks if all options do have an associated function
            len_functions_and_kwargs = len(functions_and_kwargs)
            len_functions_dictionary = len(self._functions_dictionary)
            if not len_functions_and_kwargs == len_functions_dictionary:
                raise ValueError("The number of functions must be equal to the number of available options ({} to {})."
                                 .format(len_functions_and_kwargs, len_functions_dictionary))

            # Insert the options in order, from the first option to the last.
            options_coord_list = sorted(  list(self._functions_dictionary.keys())  )
            for i, option_key in enumerate(options_coord_list):
                option_function = functions_and_kwargs[i][0]
                option_kwargs = functions_and_kwargs[i][1]

                self._functions_dictionary[option_key] = {
                    "option": self._functions_dictionary[option_key],
                    "function": option_function,
                    "kwargs": option_kwargs
                }

        # This is to insert functions on the option.
        elif type(functions_and_kwargs) == tuple:
            option_key = functions_and_kwargs[0]
            option_function = functions_and_kwargs[1]
            option_kwargs = functions_and_kwargs[2]

            self._functions_dictionary[option_key] = {
                "option": self._functions_dictionary[option_key],
                "function": option_function,
                "kwargs": option_kwargs
            }




        else:
            raise TypeError("Supports types are: list[tuple[Callable, dict]] | tuple[Callable, dict")


    def show_frame_menu(self):
        """Print the menu"""

        show_menu = self._options_list[0: 3]

        page = self._cursor_coordinates[0] + 3
        page_menu: list | tuple = self._options_list[page]

        for i, row_menu in enumerate(page_menu):
            if i % 2 == 0:
                show_menu.append("".join(row_menu))
            else:
                r = ["".join(element) if type(element) == list else element  for element in row_menu]
                show_menu.append("".join(r))

        show_menu.append(self._options_list[-1])
        print("\n".join(show_menu))


    def control_menu(self, input_user: str):
        """
        Update coord with ``input_user``

        Parameters:
             input_user : str
        """

        coord_z = 0
        coord_y = 1
        coord_x = 2

        # Move the cursor
        # Initial position
        after_coord = self._cursor_coordinates

        # Set the maximum values that the coordinates must have
        limit_coord = (self._number_pages,
                       self._options_rows_per_page,
                       self._option_per_column)

        # Obtain the coord value change
        if input_user.upper() == OK_BUTTON:
            # If the coord exist and the option has a functions
            if (after_coord in self._functions_dictionary
                and type(self._functions_dictionary[after_coord]) == dict):

                name_option = self._functions_dictionary[after_coord]["option"]
                call_function = self._functions_dictionary[after_coord]["function"]
                kwargs = self._functions_dictionary[after_coord]["kwargs"]

                call_function(**kwargs)
                return name_option

            # If only the coord exist
            elif after_coord in self._functions_dictionary:
                name_option = self._functions_dictionary[after_coord]

                return name_option

            else:
                return ""

        elif input_user.upper() == MOVE_UP:
            add_coord = (0, -1, 0)
        elif input_user.upper() == MOVE_DOWN:
            add_coord = (0, 1, 0)
        elif input_user.upper() == MOVE_LEFT:
            add_coord = (0, 0, -1)
        elif input_user.upper() == MOVE_RIGHT:
            add_coord = (0, 0, 1)
        else:
            return ""

        # sum the last coord
        last_coord = list(
            map(lambda x, y: x + y, after_coord, add_coord)
        )

        # Refactor with the coord limit
        # Refactor column value
        last_coord[coord_x] %= limit_coord[coord_x]

        # Change page
        if last_coord[coord_y] < 0 or last_coord[coord_y] >= limit_coord[coord_y]:
            last_coord[coord_z] += add_coord[coord_y]

        # Refactor column and row values
        last_coord[coord_y] %= limit_coord[coord_y]
        last_coord[coord_z] %= limit_coord[coord_z]


        # Change menu values
        self._cursor_coordinates = tuple(last_coord)

        # noinspection PyTypeChecker
        self.__setitem__((*after_coord, 0), self._cursor[False])

        # noinspection PyTypeChecker
        self.__setitem__((*last_coord, 0), self._cursor[True])

        return ""


    def _indexes_error(self, input_indexes: list | tuple):
        size_index = len(input_indexes)

        within_page_lt = bool(input_indexes[0] >= self._number_pages)
        within_row_lt = bool(input_indexes[1] >= self._options_rows_per_page)
        within_col_lt = bool(input_indexes[2] >= self._option_per_column)

        if size_index == 4 and (within_page_lt or within_row_lt or within_col_lt):
            raise IndexError(
                "The max value for input index: {}\n"
                "Entered index: {}\n".format(
                    (self._number_pages - 1,
                     self._options_rows_per_page - 1,
                     self._option_per_column - 1,
                     1),
                    input_indexes)
            )

        within_row_lt = bool(input_indexes[1] >= self._total_rows_body_menu)
        if size_index == 3 and (within_page_lt or within_row_lt or within_col_lt):
            raise IndexError(
                "The max value for input index: {}\n"
                "Entered index: {}\n".format(
                    (self._number_pages - 1,
                     self._options_rows_per_page - 1,
                     self._option_per_column - 1),
                    input_indexes)
            )

        return None


    @staticmethod
    def _input_validator(validator: Callable[[str], bool], msg: str = ""):

        entry_to_be_validated = input(msg)

        while not validator(entry_to_be_validated):
            entry_to_be_validated = input(msg)

        return entry_to_be_validated


    @staticmethod
    def _convert_str_coord_to_tuple_coord(str_coord: str):
        replace_chars = str.maketrans("", "", "()")

        str_coord = str_coord.translate(replace_chars)
        tuple_coord = tuple([int(n) for n in str_coord.split(",")])

        return tuple_coord


    @staticmethod
    def _fit_word_width(word: str, width_requested: int, tail_char: str, char_fill: str):
        if len(word) > width_requested:
            return word[:width_requested - len(tail_char)] + tail_char
        elif len(word) < width_requested:
            return word + char_fill * (width_requested - len(word))
        else:
            return word