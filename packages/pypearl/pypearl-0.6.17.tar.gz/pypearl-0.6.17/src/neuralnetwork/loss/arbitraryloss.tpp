#ifndef ArbitraryLoss_TPP
#define ArbitraryLoss_TPP

#include <cmath>

#include "arbitraryloss.hpp"

template <typename NumType>
NumType lossForward(Array<NumType, 2>* inputs, LossStruct<NumType>& loss, void* y_true){
    if(loss.type == 0x0){
        const auto* y_i1 = static_cast<const Array<int,1>*>(y_true);

        Array<NumType, 1> totals(inputs->shape[0]);
        
        for(size_t i = 0; i < inputs->shape[0]; i++){
            totals[i] = std::fmax(std::fmin(inputs->fastGet2D(i, y_i1->fastGet1D(i)),1),0);
        } 
        
        NumType sum = 0.0f;

        for(size_t i = 0; i < inputs->shape[0]; i++){
            sum+=  -log(totals.fastGet1D(i));
        }


        return sum/(inputs->shape[0]);
    }

}

template <typename NumType>
Array<NumType, 2>* lossBackward(Array<NumType, 2>* inputs, LossStruct<NumType>& loss, void* y_true){
    if(loss.type == 0x0){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 

        loss.dinputs = p;

        const auto* y_idx = static_cast<Array<int, 1>*>(y_true);

        const NumType invN = NumType(1) / NumType(inputs->shape[0]);

        const NumType eps  = NumType(1e-12);


        for (size_t i = 0; i < inputs->shape[0]; ++i) {
            NumType pyi = inputs->fastGet2D(i, y_idx->fastGet1D(i));
            if (pyi < eps) pyi = eps;
            loss.dinputs->fastSet2D(i, y_idx->fastGet1D(i), -invN / pyi);
        }

        return loss.dinputs;

    }
    /*if(loss.type == 0x1){

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 

        loss.dinputs = p;

        for (size_t i = 0; i < inputs->shape[0]; i++) {

            for (size_t j = 0; j < inputs->shape[1]; j++) {
                loss.dinputs->fastSet2D(i, j, inputs->fastGet2D(i, j));

                if (j == y_true[i]) {
                    loss.dinputs->fastInc2D(i, j, -1.0f);
                }

                loss.dinputs->fastSet2D(i, j, loss.dinputs->fastGet2D(i, j)/inputs->shape[0]);
            }
        }

        return loss.dinputs;
    }*/
}

#endif