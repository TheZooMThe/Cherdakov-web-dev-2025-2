import subprocess
import pytest

INTERPRETER = 'python'

def run_script(filename, input_data=None):
    proc = subprocess.run(
        [INTERPRETER, filename],
        input='\n'.join(input_data if input_data else []),
        capture_output=True,
        text=True,
        check=False
    )
    return proc.stdout.strip()

test_data = {
    'python_if_else': [
        ('1', 'Weird'),
        ('4', 'Not Weird'),
        ('3', 'Weird'),
        ('6','Weird'),
        ('22', 'Not Weird')
    ],
    'arithmetic_operators': [
        (['1', '2'], ['3', '-1', '2']),
        (['10', '5'], ['15', '5', '50'])
    ],
    'division': [
        (['3', '5'], ['0', '0.6']),
        (['10', '5'], ['2', '2.0']),
        (['10', '0'], ['Деление на ноль'])
    ],
    'loops': [
        (['3'], ['0', '1', '4']),
        (['5'], ['0', '1', '4', '9', '16']),
        (['-1'], [''])
    ]
    ,
    'print_function': [
        (['5'], ['12345']),
        (['-5'], ['']),
        (['10'], ['12345678910'])
    ],
    'second_score': [
        (['5', '2 5 6 2 7'], ['6']),
        (['0'], ['']),
        (['7', '1 9 2 5 6 2 8'], ['8'])
    ],
    'nested_list': [
        (['5', 'Ник', '6', 'Грег', '25', 'Найлз', '17', 'Майк', '6', 'Соник', '56.1'], ['Найлз']),
        (['6'], ['']),
        (['5', 'Ник', '67', 'Грег', '25', 'Найлз', '17', 'Майк', '67', 'Соник', '56.1'], ['Грег']),
    ],
    'lists': [
        (['4', 'append 1', 'append 2', 'insert 1 3', 'print'], ['[1, 3, 2]']),
        (['-1'], ['']),
        (['12', 'insert 0 5', 'insert 1 10', 'insert 0 6', 'print', 'remove 6', 'append 9', 'append 1', 'sort', 'print', 'pop', 'reverse', 'print'], ['[6, 5, 10]','[1, 5, 9, 10]','[9, 5, 1]'])
    ],
    'swap_case': [
        (['Www.MosPolytech.ru'], ['wWW.mOSpOLYTECH.RU']),
        (['-1'], ['-1']),
        (['Pythonist 2'], ['pYTHONIST 2']),
        (['Hello, World! 123'], ['hELLO, wORLD! 123']),  
        ([''], ['']),                                
        (['АБВГД'], ['абвгд']),                   
        (['I LoVe PolyteCh'], ['i lOvE pOLYTEcH'])                       
    ],

    'split_and_join': [
        (['this is a string'], ['this-is-a-string']),
        (['1 2 3 1'], ['1-2-3-1']),
        (['Pythonist 2'], ['Pythonist-2'])
    ],
    'max_word': [
        ([''], ['сосредоточенности']),
    ],
    'price_sum': [
        ([''], ['6842.84 5891.06 6810.9'])
    ],
    'anagram': [
        (['лист', 'слит'], ['Yes']),
        (['пила','липа'], ['Yes']),
        (['море', 'рома'], ['No']),
        (['школа', 'лошака'], ['No']),
        (['кот', 'сок'], ['No']),
        (['колос', 'сокол'], ['Yes']),
        (['123', '321'], ['Yes'])
    ],
    'metro': [
        (['5', '0 10', '5 15', '10 20', '15 25', '20 30','10'], ['3']),
        (['3','1 5', '2 6', '4 8', '4'], ['3']),
        (['море'], [''])
    ],
    'is_leap': [
        (['2024'], ['True']),
        (['1900'], ['False']),
        (['море'], [''])
    ],
    'happiness': [
        (['4 2', '1 2 1 2', '1','2'], ['0']),
        (['1 1', '5','5','10'], ['1']),
        (['3 2', '7 7 7', '1 3', ' 5 7'], ['-3'])
    ],
    'pirate_ship': [
        (['50 3', 'Золото 30 100', 'Серебро 30 90', 'Кубки 10 50'], ['Золото 30.0 100.0','Кубки 10.0 50.0', 'Серебро 10.0 30.0']),
        (['50 3','Золото 30 100', 'Серебро 20 60', 'Кубки 10 50'], ['Золото 30.0 100.0', 'Кубки 10.0 50.0', 'Серебро 10.0 30.0']),
        (['30 1', 'Золото 50 100'], ['Золото 30.0 60.0'])
    ],
    'matrix_mult': [
        (['2', '1 2', '3 4', '5 6', '7 8'], ['19 22','43 50']),
        (['3','1 0 0', '0 1 0','0 0 1', '2 3 4','5 6 7', '8 9 1'], ['2 3 4', '5 6 7', '8 9 1']),
        (['море'], [''])
    ],
    'minion_game': [
        (['BANANA'], ['Стёарт 12']),
        (['AAAAA'], ['Кевин 15']),
        (['BA'], ['Стёарт 2'])
    ],
}

def test_hello_world():
    assert run_script('hello.py') == 'Hello, world!'

@pytest.mark.parametrize("input_data, expected", test_data['python_if_else'])
def test_python_if_else(input_data, expected):
    assert run_script('python_if_else.py', [input_data]) == expected

@pytest.mark.parametrize("input_data, expected", test_data['arithmetic_operators'])
def test_arithmetic_operators(input_data, expected):
    assert run_script('arithmetic_operators.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['division'])
def test_division(input_data, expected):
    assert run_script('division.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['loops'])
def test_loops(input_data, expected):
    assert run_script('loops.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['print_function'])
def test_print_function(input_data, expected):
    assert run_script('print_function.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['second_score'])
def test_second_score(input_data, expected):
    assert run_script('second_score.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['nested_list'])
def test_nested_list(input_data, expected):
    assert run_script('nested_list.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['lists'])
def test_list(input_data, expected):
    assert run_script('lists.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['swap_case'])
def test_swap_case(input_data, expected):
    assert run_script('swap_case.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['split_and_join'])
def test_split_and_join(input_data, expected):
    assert run_script('split_and_join.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['max_word'])
def test_max_word(input_data, expected):
    assert run_script('max_word.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['price_sum'])
def test_price_sum(input_data, expected):
    assert run_script('price_sum.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['anagram'])
def test_anagram(input_data, expected):
    assert run_script('anagram.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['metro'])
def test_metro(input_data, expected):
    assert run_script('metro.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['is_leap'])
def test_is_leap(input_data, expected):
    assert run_script('is_leap.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['happiness'])
def test_is_happiness(input_data, expected):
    assert run_script('happiness.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['pirate_ship'])
def test_pirate_ship(input_data, expected):
    assert run_script('pirate_ship.py', input_data).split('\n') == expected


@pytest.mark.parametrize("input_data, expected", test_data['matrix_mult'])
def test_matrix_mult(input_data, expected):
    assert run_script('matrix_mult.py', input_data).split('\n') == expected

@pytest.mark.parametrize("input_data, expected", test_data['minion_game'])
def test_minion_game(input_data, expected):
    assert run_script('minion_game.py', input_data).split('\n') == expected

