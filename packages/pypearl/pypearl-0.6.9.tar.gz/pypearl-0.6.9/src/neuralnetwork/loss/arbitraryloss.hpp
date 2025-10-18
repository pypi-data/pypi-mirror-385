#ifndef ArbitraryLoss_HPP
#define ArbitraryLoss_HPP

#include "../../matrix/matrix.hpp"


template <typename NumType = float>
struct LossStruct {
    /*
     * Types:
     * 0x0: CCE Loss (Unfused with softmax)
     */
    uint8_t type;
    Array<NumType,2>* saved_inputs;

    // Will always be Array<NumType, 2> or Array<int, 1>, I believe it shouldn't effect efficiency as it will always be cast in switch statements.
    void* y_true;

    Array<NumType, 2>* dinputs;

};

template <typename NumType>
NumType lossForward(Array<NumType, 2>* inputs, LossStruct<NumType>& layer, void* y_true);


// The arguments technically aren't needed and you can just copy in the previous function but that makes lossForward n->n^2 in some cases
template <typename NumType>
Array<NumType, 2>* lossBackward(Array<NumType, 2>* inputs, LossStruct<NumType>& layer, void* y_true);

#include "arbitraryloss.tpp"

#endif