#ifndef ArbitraryActivation_TPP
#define ArbitraryActivation_TPP

#include "arbitraryactivation.hpp"
#include "../../matrix/matrix.hpp"
#include <cstdint>

// WHEN WRAPPED TO PYTHON YOU DO NOT OWN OUTPUTS OUTPUTS WILL BE KILLED BY THE PYTHON INTERPRETER IF LOGITS = OUTPUTS SAVE INPUTS IF AN ACTIVATION NEEDS BOTH SAVE BOTH

ndarray* activationForward(ndarray* inputs, ActivationLayer& layer){
    // Switch to binary search after 4-6 activations are finished
    if(!(&layer)){
        return NULL;
    }

    if(layer.outputs){
        Py_DECREF(layer.outputs);
    }

    if(layer.saved_inputs){
        Py_DECREF(layer.saved_inputs);
    }
    ndarray* logits = arrayCInit(0x2, inputs->dtype, inputs->dims);
    layer.saved_inputs = logits;
    
    ndarray* pout = arrayCInit(0x2, inputs->dtype, inputs->dims);
    layer.outputs = pout;

    // ReLU Arbitrary Minimum
    if(layer.type == 0x0){
            // This is split outside of the loop rather than inside because creating n^2 boolean checks/branching operations is insane and I'm not gonna trust compiler optimizers on this one since in theory it's not the same thing but only an exploit would change anything but whatever this applies to everywhere in this file I'm only writing this once so deal with it ig shoutout casey muratori
            if(inputs->dtype == 0x0){
                double relmind;
                float val;

                fastScalar8(layer.relmin, &relmind);

                float relmin = (float)relmind;

                for(size_t i = 0; i < inputs->dims[0]; i++){
                    for(size_t j = 0; j < inputs->dims[1]; j++){
                        fastMove2D4(inputs, i, j, layer.saved_inputs, i, j);
                        fastGet2D4(inputs, i, j, &val);
                        if(val < relmin){
                            fastSet2D4(layer.outputs, i, j, &relmin);
                        }
                        else{
                            fastMove2D4(inputs, i, j, layer.outputs, i, j);
                        }
                    }
                }
            }
            else if(inputs->dtype == 0x1){
                double relmin;
                double val;

                fastScalar8(layer.relmin, &relmin);

                for(size_t i = 0; i < inputs->dims[0]; i++){
                    for(size_t j = 0; j < inputs->dims[1]; j++){
                        fastMove2D8(inputs, i, j, layer.saved_inputs, i, j);
                        fastGet2D8(inputs, i, j, &val);
                        if(val < relmin){
                            fastSet2D8(layer.outputs, i, j, &relmin);
                        }
                        else{
                            fastMove2D8(inputs, i, j, layer.outputs, i, j);
                        }
                    }
                }
            }
            else{
                return nullptr;
            }
            Py_INCREF(layer.outputs);
            return layer.outputs;
    }
    
    // ReLU 0 Minimum
    if(layer.type == 0x1){
        if(inputs->dtype == 0x0){
            float zero = 0x0;
            float val = 0x0;
            for(size_t i = 0; i < inputs->dims[0]; i++){
                for(size_t j = 0; j < inputs->dims[1]; j++){
                    fastMove2D4(inputs, i, j, layer.saved_inputs, i, j);
                    fastGet2D4(inputs, i, j, &val);
                    if(val < 0x0){
                        fastSet2D4(layer.outputs, i, j, &zero);
                    }
                    else{
                        fastMove2D4(inputs, i, j, layer.outputs, i, j);
                    }
                }
            }
        }
        if(inputs->dtype == 0x1){
            double zero = 0x0;
            double val = 0x0;
            for(size_t i = 0; i < inputs->dims[0]; i++){
                for(size_t j = 0; j < inputs->dims[1]; j++){
                    fastMove2D8(inputs, i, j, layer.saved_inputs, i, j);
                    fastGet2D8(inputs, i, j, &val);
                    if(val < 0x0){
                        fastSet2D8(layer.outputs, i, j, &zero);
                    }
                    else{
                        fastMove2D8(inputs, i, j, layer.outputs, i, j);
                    }
                }
            }
        }

        return layer.outputs;
    }
    
    // Softmax
    if(layer.type == 0x2){

        if(inputs->dtype == 0x0){

            for(int i = 0; i < inputs->dims[0]; i++){
                float sum = 0.0f;
                float max;
                fastGet2D4(inputs, i, 0, &max);
                float temp;
                for(size_t j = 1; j < inputs->dims[1]; j++){
                    fastGet2D4(inputs, i, j, &temp);
                    if(max < temp){
                        max = temp;
                    }
                }
                for(size_t j = 0; j < inputs->dims[1]; j++){
                    float temp;
                    fastGet2D4(inputs, i, j, &temp);
                    temp -= max;
                    temp = exp(temp);
                    fastSet2D4(layer.outputs, i, j, &temp);
                    sum += temp;
                }
                for(size_t j = 0; j < inputs->dims[1]; j++){
                    float temp;
                    fastGet2D4(layer.outputs, i, j, &temp);
                    temp /= sum;
                    fastSet2D4(layer.outputs, i, j, &temp);
                    fastSet2D4(layer.saved_inputs, i, j, &temp);
                }
            }
            return layer.outputs;
        }
    }
   
    // Leaky ReLU
    if(layer.type == 0x3){
        if(inputs->dtype == 0x0){     
            float temp;

            double relmind;
            fastScalar8(layer.relmin, &relmind);
            float relmin = (float)relmind;

            double alphad;
            fastScalar8(layer.alpha, &alphad);
            float alpha = (float)alphad;


            for(size_t i = 0; i < inputs->dims[0]; i++){
                for(size_t j = 0; j < inputs->dims[1]; j++){
                    fastMove2D4(inputs, i, j, layer.saved_inputs, i, j);
                    fastGet2D4(inputs, i, j, &temp);
                    if(temp < relmin){
                        temp -= relmin;
                        temp *= alpha;
                        temp += relmin;
                        fastSet2D4(layer.outputs, i, j, &temp);
                    }
                    else{
                        fastMove2D4(inputs, i, j, layer.outputs, i, j);
                    }
                }
            }
            return layer.outputs;
        }
    }
    
    // Copied Linear
    if(layer.type == 0x4){
        if(inputs->dtype == 0x0){
            for(size_t i = 0; i < inputs->dims[0]; i ++){
                for(size_t j = 0; j < inputs->dims[1]; j++){
                    fastMove2D4(inputs, i, j, layer.outputs, i, j);
                    fastMove2D4(inputs, i, j, layer.saved_inputs, i, j);
                }
            }
            return layer.outputs;
        }
    }
    
    // Flow Linear
    if(layer.type == 0x5){
        Py_INCREF(inputs);
        return inputs;
    }
    
    // Sigmoid
    if(layer.type == 0x6){
        std::cout << "HERE" << std::endl;

        if(inputs->dtype == 0x0){
            std::cout << "HERE" << std::endl;
            float temp;
            for(size_t i = 0; i < inputs->dims[0]; i++){
                for(size_t j = 0; j < inputs->dims[1]; j++){
                    fastGet2D4(inputs, i, j, &temp);
                    temp = 1/(1+exp(-temp)); // there's gotta be some random demonic bit shift to do this faster
                    fastSet2D4(layer.outputs, i, j, &temp);
                    fastSet2D4(layer.saved_inputs, i, j, &temp);
                }
            }

            return layer.outputs;

        }
    }
    
    // Step
    if(layer.type == 0x7){
        if(inputs->dtype == 0x0){
            float temp;

            double relmind;
            fastScalar8(layer.relmin, &relmind);
            float relmin = (float)relmind;

            double alphad;
            fastScalar8(layer.alpha, &alphad);
            float alpha = (float)alphad;

            double betad;
            fastScalar8(layer.alpha, &betad);
            float beta = (float)beta;

            for(int i = 0; i < inputs->dims[0]; i++){
                for(int j = 0; j < inputs->dims[1]; j++){
                    fastGet2D4(inputs, i, j, &temp);
                    if(temp > relmin){
                        fastSet2D4(layer.outputs, i, j, &alpha);
                    }
                    else{
                        fastSet2D4(layer.outputs, i, j, &beta);
                    }
                }
            }
            return layer.outputs;
        }
    }
    /*
    // Single Alpha PReLU
    if(layer.type == 0x8){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(int i = 0; i < inputs->shape[0]; i++){
            for(int j = 0; j < inputs->shape[1]; j++){
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                if(inputs->fastGet2D(i, j) < layer.relmin){
                    layer.outputs->fastSet2D(i, j, (inputs->fastGet2D(i, j)-layer.relmin)*layer.alpha+layer.relmin);
                }
                else{
                    layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                }
            }
        }
        return layer.outputs;
    }

    // Array Length Alpha PReLU
    if(layer.type == 0x9){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;


    }

    // Slope Linear
    if(layer.type == 0xa){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(size_t i = 0; i < inputs->shape[0]; i ++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j)*layer.alpha);
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
            }
        }
        return layer.outputs;
    }
    
    if(layer.type == 0xb){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;

        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;

        for(size_t i = 0; i < inputs->shape[0]; i ++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i, j)*layer.alpha+layer.beta);
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
            }
        }
        return layer.outputs;
    }

    // Reverse ReLU
    if(layer.type == 0xc){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(inputs->shape); 
        layer.saved_inputs = p;


        void* memout = std::malloc(sizeof(Array<NumType,2>));
        if (!memout) throw std::bad_alloc{};
        auto* pout = new (memout) Array<NumType,2>(inputs->shape); 
        layer.outputs = pout;


        for(size_t i = 0; i < inputs->shape[0]; i++){
            for(size_t j = 0; j < inputs->shape[1]; j++){
                layer.saved_inputs->fastSet2D(i, j, inputs->fastGet2D(i, j));
                if(inputs->fastGet2D(i, j) > layer.relmin){
                    layer.outputs->fastSet2D(i, j, layer.relmin);
                }
                else{
                    layer.outputs->fastSet2D(i, j, inputs->fastGet2D(i,j));
                }
            }
        }
        return layer.outputs;
    }
    */

    return nullptr;
}


ndarray* activationBackward(ndarray* dvalues, ActivationLayer& layer){

    if(layer.dinputs){
        Py_DECREF(layer.dinputs);
    }
    if(!layer.saved_inputs){

        return nullptr;

    }

    ndarray* din = arrayCInit(0x2, layer.saved_inputs->dtype, layer.saved_inputs->dims);
    layer.dinputs = din;


    // ReLU Arbitrary Minimum
    if(layer.type == 0x0){
        if(!layer.saved_inputs){

            return nullptr;

        }
        

        if(layer.saved_inputs->dtype == 0x0){
            float val = 0.0f;
            double relmind;
            fastScalar8(layer.relmin, &relmind);
            float relmin = (float)relmind;
            for(size_t i = 0; i < layer.saved_inputs->dims[0]; i++){
                for(size_t j = 0; j < layer.saved_inputs->dims[1]; j++){
                    fastGet2D4(layer.saved_inputs, i, j, &val);
                    if(val <= relmin){
                        fastSet2D4(layer.dinputs, i, j, &val);
                    }
                    else{
                        fastMove2D4(dvalues, i, j, layer.dinputs, i, j);
                    }
                }
            }
        }
        if(layer.saved_inputs->dtype == 0x1){
            double val = 0.0f;
            double relmin;
            fastScalar8(layer.relmin, &relmin);
            for(size_t i = 0; i < layer.saved_inputs->dims[0]; i++){
                for(size_t j = 0; j < layer.saved_inputs->dims[1]; j++){
                    fastGet2D8(layer.saved_inputs, i, j, &val);
                    if(val <= relmin){
                        fastSet2D8(layer.dinputs, i, j, &val);
                    }
                    else{
                        fastMove2D8(dvalues, i, j, layer.dinputs, i, j);
                    }
                }
            }
        }

        return layer.dinputs;
    }
    
    // ReLU 0 Minimum
    if(layer.type == 0x1){
        if(!layer.saved_inputs){
            return nullptr;
        }
        if(layer.saved_inputs->dtype == 0x0){
            float val = 0.0f;
            for(size_t i = 0; i < layer.saved_inputs->dims[0]; i++){
                for(size_t j = 0; j < layer.saved_inputs->dims[1]; j++){
                    fastGet2D4(layer.saved_inputs, i, j, &val);
                    if(val <= 0x0){
                        fastSet2D4(layer.dinputs, i, j, &val);
                    }
                    else{
                        fastMove2D4(dvalues, i, j, layer.dinputs, i, j);
                    }
                }
            }
        }
        if(layer.saved_inputs->dtype == 0x1){
            double val = 0.0f;
            for(size_t i = 0; i < layer.saved_inputs->dims[0]; i++){
                for(size_t j = 0; j < layer.saved_inputs->dims[1]; j++){
                    fastGet2D8(layer.saved_inputs, i, j, &val);
                    if(val <= 0x0){
                        fastSet2D8(layer.dinputs, i, j, &val);
                    }
                    else{
                        fastMove2D8(dvalues, i, j, layer.dinputs, i, j);
                    }
                }
            }
        }

        return layer.dinputs;
    }
    /*
    // Softmax   
    if(layer.type == 0x2){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;        

        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){

            for(int j = 0; j < layer.saved_inputs->shape[1]; j++) {
                layer.dinputs->fastSet2D(i, j, 0.0f);
                for(int k = 0; k < layer.saved_inputs->shape[1]; k++) {
                    if (k == j) {
                        layer.dinputs->fastInc2D(i, j, (layer.saved_inputs->fastGet2D(i, j) * (1 - layer.saved_inputs->fastGet2D(i, j))) * dvalues->fastGet2D(i, k));
                    } else {
                        layer.dinputs->fastInc2D(i, j, (-layer.saved_inputs->fastGet2D(i, j) * layer.saved_inputs->fastGet2D(i, k)) * dvalues->fastGet2D(i, k));  
                    }
                }
            }
        }

        return layer.dinputs;
    }
    
    // Leaky ReLU
    if(layer.type == 0x3){
        //size_t dinputsShape[2] = {saved_samples, saved_prev_layer};
        //this->dinputs = Array<NumType, 2>(dinputsShape);

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) <= layer.relmin){
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j)*layer.alpha);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j));
                }
            }
        }
        return layer.dinputs;
    }
    
    // Copied Linear
    if(layer.type == 0x4){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j));
            }
        }
        return layer.dinputs;
    }
    
    // Flow Linear
    if(layer.type == 0x5){
        return dvalues;
    }
    
    // Sigmoid
    if(layer.type == 0x6){
        //size_t dinputsShape[2] = {saved_samples, saved_prev_layer};
        //this->dinputs = Array<NumType, 2>(dinputsShape);

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(int j = 0; j < layer.saved_inputs->shape[1]; j++){
                layer.dinputs->fastSet2D(i, j, layer.saved_inputs->fastGet2D(i,j )*(1-layer.saved_inputs->fastGet2D(i, j))*dvalues->fastGet2D(i, j));
            }
        }
        return layer.dinputs;
    }
    
    // Step
    if(layer.type == 0x7){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(int j = 0; j < layer.saved_inputs->shape[1]; j++){
                // OH IF x=relmin DERIVATIVE IS UNDEFINED IN STEP???? REALLY???? OK. THEN BY SOME CANCELLATION STUFF THERE IS NO WAY TO KNOW IF X AND THE OTHER THING ARE ACTUALLY EQUAL BY SOME FLOATING POINT APPROXIMATION OF 2 VALUES SO PLEASE LEAVE ME ALONE.
                layer.dinputs->fastSet2D(i, j, 0);
            }
        }
        return layer.dinputs;

    }

    // Single Alpha PReLU
    if(layer.type == 0x8){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        layer.beta = 0.0f;
        for(int i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(int j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) < layer.relmin){
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j)*layer.alpha);
                    layer.beta += dvalues->fastGet2D(i, j)*(layer.saved_inputs->fastGet2D(i, j)-layer.relmin);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i,j));
                }
            }
        }
        return layer.dinputs;
    }

    // Array Length Alpha PReLU
    if(layer.type == 0x9){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

    }

    // Slope Linear and Slope Linear Offset (because y=mx+b dy/dx = m regardless of b == 0 || b != 0 (or I'm just bad at calc and wrote a bug))
    if(layer.type == 0xa || layer.type == 0xb){
        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;

        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i, j)*layer.alpha);
            }
        }
        return layer.dinputs;
    }

    // Reverse ReLU
    if(layer.type == 0xc){

        void* mem = std::malloc(sizeof(Array<NumType,2>));
        if (!mem) throw std::bad_alloc{};
        auto* p = new (mem) Array<NumType,2>(layer.saved_inputs->shape); 

        layer.dinputs = p;


        for(size_t i = 0; i < layer.saved_inputs->shape[0]; i++){
            for(size_t j = 0; j < layer.saved_inputs->shape[1]; j++){
                if(layer.saved_inputs->fastGet2D(i, j) >= layer.relmin){
                    layer.dinputs->fastSet2D(i, j, 0);
                }
                else{
                    layer.dinputs->fastSet2D(i, j, dvalues->fastGet2D(i,j));
                }
            }
        }
        return layer.dinputs;
    }
    */
    return nullptr;
}


// Clears Logits
void freeActivationLogits(ActivationLayer& layer){
    // Force to be false in Python
    /*
    if(layer.outputOwnership){
        delete layer.outputs;
    }

    delete layer.saved_inputs;
    delete layer.dinputs;*/
}

// Update Tuneable Params
void updateParams(ActivationLayer& layer){
    
}



#include "arbitraryactivation.tpp"
#endif
