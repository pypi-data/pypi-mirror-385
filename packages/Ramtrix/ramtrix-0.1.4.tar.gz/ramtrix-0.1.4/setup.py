from setuptools import setup, find_packages

VERSION = '0.1.4' 
DESCRIPTION = 'Ripoff Numpy'
LONG_DESCRIPTION = '''A Python library for manipulating matrices while boiling your RAM.(I promise the core functions are actually optimized and WONT boil your RAM...you still have the option though)

### Key Functions:
- **row_reduce**: Perform row reduction to echelon form.
- **inverse**: Calculate the inverse of a matrix.
- **determinant**: Calculate the determinant of a matrix.
- **LU_factorize**: Perform LU factorization on a matrix.
- **matrix_multiply**: Multiply two matrices.
- **dot**: Perform dot product on matrices or vectors.
- **add**: Add two matrices together.
- **subtract**: Subtract one matrix from another.
- **scale**: Scale a matrix by a constant.
- **cofactor**: Calculate the cofactor matrix.
- **transpose**: Get the transpose of a matrix.
- **flatten**: Flatten a matrix into a 1D list.
- **create_identity**: Create an identity matrix of a given size.
- **print_matrix**: Display a matrix in a readable format.
- **check_matrix**: Validate if the input is a proper matrix.
- **tell_version**: Get the current version of the package.
- **precise_row_reduce**: Perform row reduction with higher precision.
- **inverse_by_rows**: Calculate the inverse using row operations.
- **brute_inverse**: Calculate the inverse using an Adjoint method(Cramer method).
- **laplace_determinant**: Calculate the determinant using Laplace expansion.
- **Discrete_Fourier_Transform**: Compute the Discrete Fourier Transform from sample data.
- **components**: Finds the components of vector1 onto vector2 and orthogonal to vector2.
- **projection**: Projects vector1 onto vector2.
- **normalize**: Normalizes a given vector.

Ramtrix is perfect for educational purposes, matrix operations, and small to medium-scale linear algebra tasks. It is designed to be a lightweight alternative to larger libraries like Numpy, with a focus on simplicity and performance.
'''
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown' 

# Setting up
setup(
        name="Ramtrix", 
        version=VERSION,
        author="Ram",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,

        license="MIT",  # Recommended to declare license

        packages=find_packages(),  # Finds your package automatically (e.g. ramtrix/)

        install_requires=[],  # list of dependencies (if any)
        python_requires='>=3.8',


        keywords=['python', 'matrices', 'analysis', 'linear algebra'],
        classifiers= [
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Education",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)