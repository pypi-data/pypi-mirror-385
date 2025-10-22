#ifndef ARRAYNDTPP
#define ARRAYNDTPP

#include "array.hpp"
#include <cstddef>
#include <iostream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <functional>

using std::vector;


using std::size_t;
/*
 * This file implements the header of the same name.
 * It is likely loosely commented for my personal debugging. 
 * For thorough documentation, clear explanations, etc. use the associated header file. 
 */

// N Dimensions

// Empty constructor
template <typename ArrType, size_t dims>
Array<ArrType, dims>::Array()
: data(nullptr), stride(nullptr), shape(nullptr){
    owns = false;
}

//public constructor
template <typename ArrType, size_t dims>
Array<ArrType, dims>::Array(const std::size_t* s)
{
    owns = true;
    std::size_t total = 1;
    shape = new std::size_t[dims];
    for (std::size_t i = 0; i < dims; ++i) {
        shape[i] = s[i];
        total *= shape[i];
    }

    stride = new std::size_t[dims];
    stride[dims-1] = 1;
    
    for(int i = int(dims)-2; i >= 0; --i){
        stride[i] = stride[i+1] * shape[i+1];
    }

    data = new ArrType[total]();
}

// copy constructor
template <typename ArrType, size_t dims>
Array<ArrType, dims>::Array(Array<ArrType, dims> const& other){
    owns = true;

    if (!other.shape || !other.stride || !other.data) {
        shape = nullptr;
        stride = nullptr;
        data = nullptr;
        return;
    }


    size_t total = 1;

    shape = new size_t[dims];
    stride = new size_t[dims];

    for(size_t i = 0; i < dims; i++){
        shape[i] = other.shape[i];
        total*=shape[i];
    }
    stride[dims-1] = 1;
    for (long i = dims-2; i >= 0; --i)
        stride[i] = shape[i+1] * stride[i+1];
    
    data = new ArrType[total];
    
    for(size_t i = 0; i < total; i++){
        size_t newI = i;
        size_t loc = 0;
        for (int k = dims - 1; k >= 0; --k) {
            loc   += other.stride[k] * (newI % other.shape[k]);
            newI  /= other.shape[k];
        }

        data[i] = other.data[loc];
    }

}
// Move constructor
template<typename ArrType, size_t dims>
Array<ArrType, dims>::Array(Array&& other) noexcept
    : data(other.data), stride(other.stride), owns(other.owns), shape(other.shape)
{
    other.data = nullptr;
    other.shape = nullptr;
    other.stride = nullptr;
    other.owns = false;
}


//delete
template <typename ArrType, std::size_t dims>
Array<ArrType, dims>::~Array() {
    if(owns){
        delete[] data;
    }
    delete[] stride;
    delete[] shape;
}

//should be private constructor
template <typename ArrType, std::size_t dims>
Array<ArrType, dims>::Array(ArrType* d, std::size_t* _stride, std::size_t* _shape)
: data(d), owns(false)
    {
        shape = new std::size_t[dims];
        stride = new std::size_t[dims];
        for(std::size_t i = 0; i < dims; i++){
            shape[i] = _shape[i];
            stride[i] = _stride[i];
        }
    }

//should be private constructor
template <typename ArrType, std::size_t dims>
Array<ArrType, dims>::Array(ArrType* d, std::size_t* _stride, std::size_t* _shape, bool owns)
: data(d), owns(owns)
    {
        shape = new std::size_t[dims];
        stride = new std::size_t[dims];
        for(std::size_t i = 0; i < dims; i++){
            shape[i] = _shape[i];
            stride[i] = _stride[i];
        }
    }

// [] operator override for arr[]
template <typename ArrType, std::size_t dims>
Array<ArrType, dims-1> Array<ArrType, dims>::operator[](std::size_t idx){
    if (idx >= shape[0]) throw std::out_of_range("Index out of bounds.");
    if constexpr(dims > 2){
        std::size_t newShape[dims-1];
        std::size_t newStride[dims-1];

        for(std::size_t i = 0; i < dims-1; i++){
            newShape[i] = shape[i+1];
            newStride[i] = stride[i+1];
        }

        ArrType* newData = data + idx * stride[0];
        return Array<ArrType, dims-1>(newData, newStride, newShape);
    }
    else{
        std::size_t len = shape[1];
        std::size_t s = stride[1];

        ArrType* newData = data + idx * stride[0];
        return Array<ArrType, 1>(len, s, newData);
    }
}



template <typename ArrType, std::size_t dims>
ArrType Array<ArrType, dims>::fastGet2D( std::size_t i,  std::size_t j) const{
    return data[i*stride[0]+j*stride[1]];
}

template <typename ArrType, std::size_t dims>
void Array<ArrType, dims>::fastSet2D(std::size_t i,  std::size_t j, ArrType val){
    data[i*stride[0]+j*stride[1]] = val;
}

template <typename ArrType, std::size_t dims>
void Array<ArrType, dims>::fastInc2D(std::size_t i,  std::size_t j, ArrType val){
    data[i*stride[0]+j*stride[1]] += val;
}

// same as previous, but const
template <typename ArrType, std::size_t dims>
Array<ArrType, dims-1> Array<ArrType, dims>::operator[](std::size_t idx) const{
    if (idx >= shape[0]) throw std::out_of_range("Index out of bounds.");
    if constexpr(dims > 2){
        std::size_t newShape[dims-1];
        std::size_t newStride[dims-1];

        for(std::size_t i = 0; i < dims-1; i++){
            newShape[i] = shape[i+1];
            newStride[i] = stride[i+1];
        }

        ArrType* newData = data + idx * stride[0];
        return Array<ArrType, dims-1>(newData, newStride, newShape);
    }
    else{
        std::size_t len = shape[1];
        std::size_t s = stride[1];

        ArrType* newData = data + idx * stride[0];
        return Array<ArrType, 1>(len, s, newData);
    }
}

// recursive function that returns the array visualized as a string.
template<typename ArrType, std::size_t dims>
std::string Array<ArrType, dims>::toString() const{
    if(shape[0] > 6){
        return "[\n " 
        + (*this)[0].toString() + "\n " 
        + (*this)[1].toString() + "\n " 
        + (*this)[2].toString() + "\n ... \n" 
        + (*this)[(shape[0]-3)].toString() + "\n " 
        + (*this)[(shape[0]-2)].toString() + "\n " 
        + (*this)[(shape[0]-1)].toString()+ "\n]";
    }
    else{
        std::string str = "[\n";
        for(size_t i = 0; i < shape[0]; i++){
            str += " " + (*this)[i].toString() + "\n";
        }
        str += "]";
        return str;
    }
}

// Returns a transposed VIEW of the same data.
template <typename ArrType, std::size_t dims>
Array<ArrType, dims> Array<ArrType, dims>::transpose() const{
    static_assert(dims==2, "Transpose is currently only implemented for 2D arrays.");

    std::size_t newShape[2] = { shape[1], shape[0] };
    std::size_t newStride[2] = { stride[1], stride[0] };

    return Array<ArrType, dims>(data, newStride, newShape);
}

// copies the array into a new block of memory
template <typename ArrType, std::size_t dims>
Array<ArrType, dims> Array<ArrType, dims>::copy() const{
    // This section is an O(dims) time portion that checks if the Array was unchanged/shape is default.
    // If the array is unchanged, time complexity goes from O(dims*total) to O(total).
    size_t total = 1;
    size_t* newStrides = new std::size_t[dims];
    newStrides[dims-1] = 1;
    for(size_t i = 0; i < dims; i++){
        total *= shape[i];
    }
    bool unchanged = true;
    // i is a long here because size_t is unsigned so decrementing it results in an underflow (it's always geq 0).
    for(long i = dims-2; i >= 0; i--){
        newStrides[i] = shape[i+1]*newStrides[i+1];
        if(stride[i] != shape[i+1]*stride[i+1]){
            unchanged = false;
        }
    }

    if(stride[dims-1] == 1 && unchanged){
        // This is the function call that optimizes copying arrays whose strides are default.
        return copyTurbo(total);
    }

    ArrType* newData = new ArrType[total];
    for(size_t i = 0; i < total; i++){
        size_t newI = i;
        size_t loc = 0;
        for (int k = dims - 1; k >= 0; --k) {
            loc   += stride[k] * (newI % shape[k]);
            newI  /= shape[k];
        }

        newData[i] = data[loc];
    }
    return Array<ArrType, dims>(newData, newStrides, shape, true);
    delete[] newStrides;
}

// copies data, shape and strides directly, with 0 checks for any edge cases.
template <typename ArrType, size_t dims>
Array<ArrType, dims> Array<ArrType, dims>::copyTurbo(std::size_t total) const{
    ArrType* newData = new ArrType[total];
    for(std::size_t i = 0; i < total; i++){
        newData[i] = data[i]; 
    }
    return Array<ArrType, dims>(newData, stride, shape, true);
}

// Scalar multiplication
template <typename ArrType, size_t dims>
void Array<ArrType, dims>::operator*=(ArrType num){
    static_assert(std::is_arithmetic_v<ArrType>,"Scalar multiplication is currently only available for numerical types.");

    size_t total = 1;
    for(size_t i = 0; i < dims; i++){
        total *= shape[i];
    }
    
    bool unchanged = true;
    // i is a long here because size_t is unsigned so decrementing it results in an underflow (it's always geq 0).
    for(long i = dims-2; i >= 0; i--){
        if(stride[i] != shape[i+1]*stride[i+1]){
            unchanged = false;
        }
    }

    if(stride[dims-1] == 1 && unchanged){
        // This is the function call that optimizes copying arrays whose strides are default.
        return scalarMultTurbo(num, total);
    }

    // Copied and pasted from copy()
    for(size_t i = 0; i < total; i++){
        size_t newI = i;
        size_t loc = 0;
        for (int k = dims - 1; k >= 0; --k) {
            loc   += stride[k] * (newI % shape[k]);
            newI  /= shape[k];
        }

        data[loc] *= num;
    }
    return;

}

// Fast scalar mult for simple arrays
template <typename ArrType, size_t dims>
void Array<ArrType, dims>::scalarMultTurbo(ArrType num, size_t total){
    for(size_t i = 0; i < total; i++){
        data[i] *= num;
    }
    return;
}

// Scalar addition
template <typename ArrType, size_t dims>
void Array<ArrType, dims>::operator+=(ArrType num){
    static_assert(std::is_arithmetic_v<ArrType>,"Scalar multiplication is currently only available for numerical types.");

    size_t total = 1;
    for(size_t i = 0; i < dims; i++){
        total *= shape[i];
    }
    
    bool unchanged = true;
    // i is a long here because size_t is unsigned so decrementing it results in an underflow (it's always geq 0).
    for(long i = dims-2; i >= 0; i--){
        if(stride[i] != shape[i+1]*stride[i+1]){
            unchanged = false;
        }
    }

    if(stride[dims-1] == 1 && unchanged){
        // This is the function call that optimizes copying arrays whose strides are default.
        return scalarAddTurbo(num, total);
    }

    // Copied and pasted from copy()
    for(size_t i = 0; i < total; i++){
        size_t newI = i;
        size_t loc = 0;
        for (int k = dims - 1; k >= 0; --k) {
            loc   += stride[k] * (newI % shape[k]);
            newI  /= shape[k];
        }

        data[loc] += num;
    }
    return;

}

// Fast scalar addition for simple arrays
template <typename ArrType, size_t dims>
void Array<ArrType, dims>::scalarAddTurbo(ArrType num, size_t total){
    for(size_t i = 0; i < total; i++){
        data[i] += num;
    }
    return;
}

// Returns an array of the same shape but zeroed out
template <typename ArrType, size_t dims>
Array<ArrType, dims> Array<ArrType, dims>::zeros(){
    return Array<ArrType, dims>(shape);
}

// Dot product nxm matrix dot (m length vector)^T, vector treated as a column, returns nx1 matrix, used for multithreading
template <typename ArrType>
void dotVector(const Array<ArrType, 1>& vector, const Array<ArrType, 2>& A, Array<ArrType, 2>& C, size_t i){
    if(A.shape[1] != vector.len){
        throw std::length_error("Shape Error: Vector length must be length of rows in matrix");
    }
    size_t newShape[2] = { A.shape[0], 1 };
    for(size_t j = 0; j < A.shape[0]; j++){
        C[j][i] = A[j]*vector;
    }
    
}

//The following two functions are poorly implemented and need to be seriously reworked for large scale use cases, but I wanted to get them working so I could rebuild /neuralnetwork on them, then rework them
// Dot product of 2 2D Matrices
template <typename ArrType, size_t dims>
Array<ArrType, dims> Array<ArrType, dims>::operator*(const Array<ArrType, dims>& B) const{
    if(dims != 2){
        throw std::length_error("Shape Error: Matrix must be 2D");
    }
    if(shape[1]!= B.shape[0]){
        throw std::length_error("Shape Error: Columns and rows are different shapes");
    }
    size_t newShape[2] = { shape[0], B.shape[1] };
    Array<ArrType, 2> C(newShape);
    auto BColMajor = B.transpose();
    /*vector<std::thread> threads;
    threads.reserve(BColMajor.shape[0]);*/

    for(size_t i = 0; i < B.shape[1]; i++){

        /*threads.emplace_back([&, i](){
            dotVector<ArrType>(BColMajor[i], *this, C, i);
        });*/
        auto col = (*this)*BColMajor[i];
        for(size_t j = 0; j < shape[0]; j++){
            C[j][i] = col[j][0];
        }
    }
    /*
    for(std::thread &t : threads){
        if(t.joinable()){
            t.join();
        }
    }*/
    return C;
}

// Dot product nxm matrix dot (m length vector)^T, vector treated as a column, returns nx1 matrix
template <typename ArrType, size_t dims>
Array<ArrType, dims> Array<ArrType, dims>::operator*(const Array<ArrType, 1>& vector) const{
    if(dims != 2){
        throw std::length_error("Shape Error: Matrix must be 2D");
    }
    if(shape[1] != vector.len){
        throw std::length_error("Shape Error: Vector length must be length of rows in matrix");
    }
    size_t newShape[2] = { shape[0], 1 };
    Array<ArrType, dims> col(newShape);
    for(size_t i = 0; i < shape[0]; i++){
        col[i][0] = (*this)[i]*vector;
    }
    return col;
}

template <typename ArrType, size_t dims>
Array<ArrType, dims>& Array<ArrType, dims>::operator=(Array<ArrType, dims> const& matrix){
    if (this == &matrix) 
        return *this;

    if(owns && data != nullptr){
        delete [] data;
    }
    if(stride != nullptr)
        delete [] stride;
    if(shape != nullptr)
        delete [] shape;
    size_t total = 1;
    size_t* newStrides = new size_t[dims];
    size_t* newShape =  new size_t[dims];
    newStrides[dims-1] = 1;
    for(size_t i = 0; i < dims; i++){
        newShape[i] = matrix.shape[i];
        total *= matrix.shape[i];
    }
    bool unchanged = true;
    // i is a long here because size_t is unsigned so decrementing it results in an underflow (it's always geq 0).
    for(long i = dims-2; i >= 0; i--){
        newStrides[i] = matrix.shape[i+1]*newStrides[i+1];
        if(matrix.stride[i] != matrix.shape[i+1]*matrix.stride[i+1]){
            unchanged = false;
        }
    }
    //uncomment to turbo charge
    /*if(stride[dims-1] == 1 && unchanged){
        // This is the function call that optimizes copying arrays whose strides are default.
        return copyTurbo(total);
    }*/

    ArrType* d = new ArrType[total];
    for(size_t i = 0; i < total; i++){
        size_t newI = i;
        size_t loc = 0;
        for (int k = dims - 1; k >= 0; --k) {
            loc   += matrix.stride[k] * (newI % matrix.shape[k]);
            newI  /= matrix.shape[k];
        }

        d[i] = matrix.data[loc];
    }
    this->data = d;
    this->owns = true;
    this->shape = newShape;
    this->stride = newStrides;
    return (*this);
}

template <typename ArrType, size_t dims>
ArrType Array<ArrType, dims>::max(){
    ArrType max = (*this)[0].max();
    for(size_t i = 1; i < shape[0]; i++){
        ArrType temp = (*this)[i].max();
        if(temp > max){
            max = temp;
        }
    }
    return max;
}

template <typename ArrType, size_t dims>
ArrType Array<ArrType, dims>::min(){
    ArrType min = (*this)[0].min();
    for(size_t i = 1; i < shape[0]; i++){
        ArrType temp = (*this)[i].min();
        if(temp < min){
            min = temp;
        }
    }
    return min;
}



#include "array1d.tpp"

#endif