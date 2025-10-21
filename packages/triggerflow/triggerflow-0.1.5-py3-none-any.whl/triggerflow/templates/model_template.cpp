#include "NN/{{MODEL_NAME}}.h"
#include "emulator.h"
#include "NN/nnet_utils/nnet_common.h"
#include <any>
#include <array>
#include <utility>
#include "ap_fixed.h"
#include "ap_int.h"
#include "scales.h"

using namespace hls4ml_{{MODEL_NAME}};

class {{MODEL_NAME}}_emulator : public hls4mlEmulator::Model {

private:
    unscaled_t _unscaled_input[N_INPUT_1_1];
    input_t _scaled_input[N_INPUT_1_1];
    result_t _result[{{N_OUTPUTS}}];

    virtual void _scaleNNInputs(unscaled_t unscaled[N_INPUT_1_1], input_t scaled[N_INPUT_1_1])
    {
        for (int i = 0; i < N_INPUT_1_1; i++)
        {
            unscaled_t tmp0 = unscaled[i] - hls4ml_{{MODEL_NAME}}::ad_offsets[i];
            input_t tmp1 = tmp0 >> hls4ml_{{MODEL_NAME}}::ad_shift[i];
            scaled[i] = tmp1;
        }
    }

public: 
    virtual void prepare_input(std::any input) {
        unscaled_t *unscaled_input_p = std::any_cast<unscaled_t*>(input);
        
        for (int i = 0; i < N_INPUT_1_1; i++) {
            _unscaled_input[i] = std::any_cast<unscaled_t>(unscaled_input_p[i]);
        }

        _scaleNNInputs(_unscaled_input, _scaled_input);
    }

    virtual void predict() {
        {{MODEL_NAME}}(_scaled_input, _result);
    }
  
    virtual void read_result(std::any result) {
        result_t *result_p = std::any_cast<result_t*>(result);
        for (int i = 0; i < {{N_OUTPUTS}}; i++) {
            result_p[i] = _result[i];
        }
    }
};

extern "C" hls4mlEmulator::Model* create_model() {
    return new {{MODEL_NAME}}_emulator;
}

extern "C" void destroy_model(hls4mlEmulator::Model* m) {
    delete m;
}
