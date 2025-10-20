set "venv=.windows_venv"
set "activate=Scripts\activate.bat"
set "activation=%venv%\%activate%"
set "libs=setuptools cython"

echo "�������� ������������� ������������ ���������..."

if exist "%venv%" (
    :venv_exist
    echo "���������� ���������..."
    call %activation%
    echo "������������� ����������..."
    pip install %libs%
    echo "�������� cython..."
    py autoproperty/setup.py build_ext --inplace
) else (
    echo "��������� �� �������. �������..."
    python -m venv %venv%
    goto venv_exist
)

echo "������ ��������"