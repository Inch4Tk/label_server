import { IS_TRAINING, IS_NOT_TRAINING } from "../actions"

const is_training = (state = {isTraining: false}, action) => {
    switch (action.type) {
        case IS_TRAINING:
            return Object.assign({}, state, {
                isTraining: true,
            });
        case IS_NOT_TRAINING:
            return Object.assign({}, state, {
                isTraining: false,
            });
        default:
            return state;
    }
};

export default is_training