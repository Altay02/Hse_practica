from django.shortcuts import render

# Create your views here.
#далее про матрицу

from .forms import MatrixForm
import numpy as np
import itertools
import collections
import copy

def canonization(a, is_root=1):
    rows_unordered_cols_ordered_separately = np.sort(a) # ordered columns in each row separately, but no rows

    str_rows_unordered_list = []
    for i in range(rows_unordered_cols_ordered_separately.shape[0]):
        str_rows_unordered_list.append(''.join(str(e) for e in rows_unordered_cols_ordered_separately[i]))

    rows_order = np.argsort(str_rows_unordered_list)
    rows_ordered = np.empty((0, a.shape[1]), int)
    for i in rows_order:
        rows_ordered = np.concatenate((rows_ordered, [a[i]]))

    # тут столбцы
    rows_ordered_separately = np.sort(rows_ordered, axis = 0) # ordered columns in each row separately, but no rows

    str_cols_unordered_list = []
    for i in range(rows_ordered_separately.shape[1]):
        str_cols_unordered_list.append(''.join(str(col) for col in rows_ordered_separately[:, i]))


    cols_order = np.argsort(str_cols_unordered_list)

    cols_ordered = np.empty((a.shape[0], 0), int) # it will really cols_ordered_rows_ordered
    for i in cols_order:
        cols_ordered = np.concatenate((cols_ordered, rows_ordered[:, i:i+1]), axis=1)



    # тут собираем более подробную информацию про разбиение на группы

    groups_tmp = collections.Counter()
    rows_group_division = []
    for row_index in rows_order:
        groups_tmp[str_rows_unordered_list[row_index]] += 1
        if (groups_tmp[str_rows_unordered_list[row_index]] == 1):
            rows_group_division.append(1)
        else:
            rows_group_division[-1] += 1

    groups_tmp = collections.Counter()

    cols_group_division = []
    for col_index in cols_order:
        groups_tmp[str_cols_unordered_list[col_index]] += 1
        if (groups_tmp[str_cols_unordered_list[col_index]] == 1):
            cols_group_division.append(1)
        else:
            cols_group_division[-1] += 1


    group_division = []
    cur_row = cur_col = 0
    max_group_count = max(len(cols_group_division), len(rows_group_division))
    for i in range(max_group_count):
        rows_count = rows_group_division[-1]
        cols_count = cols_group_division[-1]
        if i < len(rows_group_division):
            rows_count = rows_group_division[i]
            cur_row += rows_count
        if i < len(cols_group_division):
            cols_count = cols_group_division[i]
            cur_col += cols_count
        group_division.append(((cur_row - rows_count, cur_row), (cur_col - cols_count, cur_col)))

    permutations = [rows_order, cols_order]

    group_sorted_matrix = cols_ordered
    if is_root:

        for indices in group_division:
            submatrix = group_sorted_matrix[indices[0][0]:indices[0][1],indices[1][0]:indices[1][1]]
            [tmp_submatrix, group_permutation] = canonization(submatrix, 0)

            tmp_subrows = np.copy(group_sorted_matrix[indices[0][0]:indices[0][1], :])
            tmp_subRowPemutation = np.copy(rows_order[indices[0][0]:indices[0][1]])

            for row_index in range(len(tmp_subrows)):
                group_sorted_matrix[indices[0][0] + row_index] = tmp_subrows[group_permutation[0][row_index]]
                rows_order[indices[0][0] + row_index] = tmp_subRowPemutation[group_permutation[0][row_index]]

            tmp_subcols = np.copy(group_sorted_matrix[:, indices[1][0]:indices[1][1]])

            tmp_subColPemutation = np.copy(cols_order[indices[1][0]:indices[1][1]])

            for col_index in range(tmp_subcols.shape[1]):
                group_sorted_matrix[:, indices[1][0] + col_index:indices[1][0] + col_index + 1] = tmp_subcols[:, group_permutation[1][col_index]:group_permutation[1][col_index]+1]
                cols_order[indices[1][0] + col_index] = tmp_subColPemutation[group_permutation[1][col_index]]

    return [group_sorted_matrix, permutations]


def index(request):
    flag_posted = False
    # If this is a POST request then process the Form data
    if request.method == 'POST':
        flag_posted = True
        # Create a form instance and populate it with data from the request (binding):
        form = MatrixForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            matrix_numbers_string = form.cleaned_data['matrix']
            rows_size = form.cleaned_data['rows_size']
            cols_size = form.cleaned_data['cols_size']
            matrix_numbers_list = list(map(int, matrix_numbers_string.split()))
            matrix_list = []
            for row in range(rows_size):
                matrix_list.append(matrix_numbers_list[row * cols_size : (row + 1) * cols_size])
            np_matrix = np.array(matrix_list)
            canonization_result = canonization(np_matrix)
            can_np_matrix = canonization_result[0]
            # redirect to a new URL:
            context = {'matrix_string': form.cleaned_data['matrix'],
                       'matrix_list': matrix_list,
                       'can_matrix': can_np_matrix,
                       'rows_size': rows_size,
                       'cols_size': cols_size,
                       'flag_posted': flag_posted}
            return render(request, 'index.html', context)

    # If this is a GET (or any other method) create the default form.
    else:
        form = MatrixForm(initial={'matrix': 'any matrix',})

    return render(request, 'index.html', {'form': form, 'flag_posted': flag_posted})
