from mydb import MyDB

def describe_init():
    
    def it_calls_saveStrings_if_file_missing(mocker):
        mock_isfile = mocker.patch("os.path.isfile", return_value=False)
        my_mock = mocker.patch.object(MyDB, "saveStrings")

        dummydb = MyDB("dummy.db")

        mock_isfile.assert_called_once()
        my_mock.assert_called_once_with([])

    def it_doesnt_call_saveStrings_if_file_exists(mocker):
        mock_isfile = mocker.patch("os.path.isfile", return_value=True)
        my_mock = mocker.patch.object(MyDB, "saveStrings")

        db = MyDB("dummy.db")

        mock_isfile.assert_called_once()
        my_mock.assert_not_called()

def describe_load_strings_method():

    def it_returns_data_from_pickle_small_array(mocker):
        db = MyDB("dummyfile")

        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        mock_pickle = mocker.patch("pickle.load", return_value = ["first", "second"])

        result = db.loadStrings()

        assert result == ["first", "second"]
        mock_open.assert_called_once_with("dummyfile", "rb")
        mock_pickle.assert_called_once()

    def it_returns_data_from_pickle_large_array(mocker):
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        db = MyDB("dummyfile")
        
        mock_pickle = mocker.patch("pickle.load", return_value = ["Chicken", "nuggets", "are", "amazing", "and", "I", "love", "to", "eat", "them", "especially", "dino", "nuggs", "because", "they", "are", "the", "bomb"])

        result = db.loadStrings()

        assert result == ["Chicken", "nuggets", "are", "amazing", "and", "I", "love", "to", "eat", "them", "especially", "dino", "nuggs", "because", "they", "are", "the", "bomb"]
        mock_open.assert_called_once_with("dummyfile", "rb")
        mock_pickle.assert_called_once()

def describe_save_strings_method():
    
    def it_saves_data_with_small_array(mocker):
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        db = MyDB("dummyfile")

        mock_pickle = mocker.patch("pickle.dump")

        db.saveStrings(["first", "second"])
        
        mock_open.assert_called_once_with("dummyfile", "wb")
        mock_open.assert_called_once()
        args, kwargs = mock_pickle.call_args
        assert args[0] == ["first", "second"]

    def it_saves_data_with_large_array(mocker):
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        db = MyDB("dummyfile")

        mock_pickle = mocker.patch("pickle.dump")

        db.saveStrings(["Chicken", "nuggets", "are", "amazing", "and", "I", "love", "to", "eat", "them", "especially", "dino", "nuggs", "because", "they", "are", "the", "bomb"])
        
        mock_open.assert_called_once_with("dummyfile", "wb")
        mock_open.assert_called_once
        args, kwargs = mock_pickle.call_args
        assert args[0] == ["Chicken", "nuggets", "are", "amazing", "and", "I", "love", "to", "eat", "them", "especially", "dino", "nuggs", "because", "they", "are", "the", "bomb"]


        
