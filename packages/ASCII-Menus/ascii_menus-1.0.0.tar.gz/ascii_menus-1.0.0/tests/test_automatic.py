import math
import string
import unittest
from pprint import pprint

from src.ASCII_Menus import Menu, DEFAULT_CHARACTERS
import random

CHARACTER_MENU: DEFAULT_CHARACTERS = DEFAULT_CHARACTERS.copy()


def parameter_generate():
    # Generate random random_title for the menu
    width_title = random.randrange(1, 100)
    random_title = "".join(
        [random.choice(string.ascii_letters) for i in range(width_title)]
    )

    # Generate random number for column
    width_col = random.randrange(1, 18)

    # Generate random number for rows
    width_row = random.randrange(3, 50)

    # Generate random number for character por options
    n_char_options = random.randrange(1, 30)

    # Generate random list for the menu
    list_size = random.randrange(1, 1000)
    test_option_list: list = []

    for i in range(list_size):
        width_option = random.randrange(1, 100)
        option = "".join(
            [random.choice(string.ascii_letters) for j in range(width_option)]
        )
        test_option_list.append(option)
    return random_title, width_col, width_row, n_char_options, test_option_list


class TestMenu(unittest.TestCase):
    """
    def test___init__(self):

        self.assertEqual(TEST_MENU._type_menu, True)
        self.assertEqual(TEST_MENU.activated, True)
        self.assertEqual(TEST_MENU._title_menu, "test_menu")
        self.assertEqual(TEST_MENU._cursor_coordinates, [0, 0, 0])
        self.assertEqual(TEST_MENU._option_per_column, 3)
        self.assertEqual(TEST_MENU._options_rows_per_page, 4)
        self.assertEqual(TEST_MENU._character_per_option, 4)
        self.assertEqual(TEST_MENU._number_pages, 1, "{}".format(TEST_MENU._number_pages))
        self.assertEqual(TEST_MENU._max_index, 12)
        self.assertEqual(TEST_MENU._characters_per_row, 25)
        self.assertEqual(TEST_MENU._options_list, [[["|", "   ", "t... ","   " , ":    ","   " , "m... ", '\x1b[48;5;255m \x1b[0m', "|"],
                                                    ["|", "   ", "test ", "   ", ":    ", "   ", "menu ", '\x1b[48;5;255m \x1b[0m', "|"],
                                                    ["|", "   ", "test ", "   ", ":    ", "   ", "menu ", '\x1b[48;5;255m \x1b[0m', "|"],
                                                    ["|", "   ", "test ", "   ", ":    ", "   ", "menu ", '\x1b[48;5;255m \x1b[0m', "|"]]])

        random_list = []
        len_random_list = random.randrange(1, 1000)
        for n in range(len_random_list):
            len_word = random.randrange(1, 20)
            word = ""
            for nn in range(len_word):
                char = random.choice(string.ascii_lowercase)
                word += char
            random_list.append(word)

        max_option_len = max(
            map(lambda a: len(a), random_list)
        )


        print("List Created")

        for n in range(1000):
            if n % 100 == 0: print(n)

            n_columns = random.randrange(1, 100)
            n_rows = random.randrange(1, 100)
            t_n_pages = math.ceil(len_random_list / (n_columns * n_rows))
            iterative_menu = Menu("test_menu", n_columns, n_rows, max_option_len, random_list)

            # Check correct calculate to _number_pages
            self.assertEqual(iterative_menu._number_pages, t_n_pages, "{}\n{}\n{}\n{}\n".
                             format(n,
                                    len_random_list,
                                    n_columns,
                                    n_rows,
                                    iterative_menu._options_list))

            compare_list = []
            # Check _options_list Structure
            # Check number page
            self.assertEqual(len(iterative_menu._options_list), iterative_menu._number_pages, "\n{}\n{}\n{}\n{}\n{}".
                             format(n,
                                    len_random_list,
                                    n_columns,
                                    n_rows,
                                    iterative_menu._options_list))

            # Check number Rows and Columns
            for page in iterative_menu._options_list:
                # Check number Rows on page
                self.assertEqual(len(page),
                                 iterative_menu._options_rows_per_page,
                                 "\n{}\n{}\n{}\n{}"
                                 .format(n,
                                         len_random_list,
                                         n_columns,
                                         n_rows)
                                 )
                for row in page:
                    # Check number column on row
                    self.assertEqual(len(row),
                                     iterative_menu._option_per_column * 2 + 3,
                                     "\n{}\n{}\n{}\n{}\n{}"
                                     .format(n,
                                             len_random_list,
                                             n_columns,
                                             n_rows,
                                             row)
                                     )

                    # Rows has Correct RowLimit
                    compare_list.extend(row)
                    self.assertTrue(row[0] == CHARACTER_MENU["RowLimit"] and row[-1] == CHARACTER_MENU["RowLimit"],
                                    "\n{}\n{}\n{}\n{}\n{} - {}"
                                    .format(n,
                                            len_random_list,
                                            n_columns,
                                            n_rows,
                                            row[0], row[-1]
                                    )
                    )

                    # Row has Correct ScrollBarValues
                    self.assertTrue(row[-2] == CHARACTER_MENU["ScrollBarValues"][True],
                                    "\n{}\n{}\n{}\n{}\n{}"
                                    .format(n,
                                            len_random_list,
                                            n_columns,
                                            n_rows,
                                            row[-2]
                                    )
                    )

                    # Row has Correct cursor_values
                    self.assertTrue(DEFAULT_CHARACTERS["cursor_values"][False] in row[1::2],
                                    "\n{}\n{}\n{}\n{}\n{}"
                                    .format(n,
                                            len_random_list,
                                            n_columns,
                                            n_rows,
                                            row[1::2]
                                    )
                    )

            for option in random_list:
                compare_list = [word.replace(" ", "") for word in compare_list]
                self.assertTrue(option in compare_list, "Option {} not find".format(option))
    """
    """
    def test_change_coordinate_cursor(self):
        coord_x = 2
        coord_y = 1
        coord_z = 0

        keywords_possible = ("W", "S", "A", "D")
        moves_possibles = ((0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1))


        for n in range(10000):
            input_user = random.choice(keywords_possible)
            change_coord = moves_possibles[keywords_possible.index(input_user)]


            first_coord = TEST_MENU._cursor_coordinates
            last_coord = TEST_MENU._cursor_coordinates



            self.assertNotEqual(first_coord, last_coord, "{} --> {}\n{} - {}".format(first_coord, last_coord, input_user, last_coord))
            self.assertTrue(bool(last_coord[coord_x] < TEST_MENU._option_per_column), "{} < {}\n{} - {}".format(last_coord[coord_x], TEST_MENU._option_per_column, input_user, last_coord))
            self.assertTrue(bool(last_coord[coord_y] < TEST_MENU._options_rows_per_page), "{} < {}\n{} - {}".format(last_coord[coord_y], TEST_MENU._options_rows_per_page, input_user, last_coord))
            self.assertTrue(bool(last_coord[coord_z] < TEST_MENU._number_pages), "{} < {}\n{} - {}".format(last_coord[coord_z], TEST_MENU._number_pages, input_user, last_coord))
    """

    @unittest.skip
    def test___init__(self):
        def generate_menu():
            title, n_col, n_row, n_charm, options_list = parameter_generate()

            new_menu = Menu(title, n_col, n_row, n_charm, options_list)

            return new_menu


        test_menu = generate_menu()

        test_menu.show_frame_menu()

        print("Finished")


    def test_show_frame_menu(self):
        test_menu = Menu(*parameter_generate())

        for n in range(101):
            print(test_menu.show_frame_menu())
            #self.assertTrue(1 == 1)


if __name__ == "__main__":
    unittest.main()
