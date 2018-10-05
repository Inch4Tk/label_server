import React from "react";
import Autosuggest from 'react-autosuggest';

const getSuggestionValue = suggestion => suggestion;

const renderSuggestion = suggestion => (
    <span>{suggestion}</span>
);

const shouldRenderSuggestions = () => {
    return true;
}

class AutoCompleter extends React.Component {
    constructor() {
        super();
        this.state = {
            value: '',
            suggestions: [],
            index: -1
        };
        this.getSuggestions = this.getSuggestions.bind(this);
        this.onChange = this.onChange.bind(this);
        this.onSuggestionsFetchRequested = this.onSuggestionsFetchRequested.bind(this);
    }

    componentDidMount() {
        document.addEventListener('keydown', this.handle_keypress);
        this.setState({
            suggestions: this.props.suggestions
        })
    }

    getValue() {
        return this.state.value
    }

    getSuggestions (value) {
        const inputValue = value.trim().toLowerCase();
        const inputLength = inputValue.length;
        return inputLength === 0 ? this.props.suggestions : this.props.suggestions.filter(val =>
            val.toLowerCase().slice(0, inputLength) === inputValue
        );
    };

    onChange(event, {newValue, method}) {
        if (method === 'down' || method === 'up') {
            let sugg = this.state.suggestions;
            let curr_index = this.state.index;
            let new_index = -1;
            let new_sugg = this.state.value;

            if (sugg.length > 0) {
                if (method === 'up') {
                    new_index = (curr_index - 1) < 0 ? sugg.length -1 : (curr_index -1) % sugg.length;
                }
                else {
                    new_index = (curr_index + 1) % sugg.length;
                }
                new_sugg = sugg[new_index]
            }

            this.setState({
                value: new_sugg,
                index: new_index
            });
        }

        else if (method === 'enter') {
            return;
        }

        else {
            this.setState({
                value: newValue ? newValue : ''
            });
        }
    };

    onSuggestionsFetchRequested({ value }) {
        this.setState({
            suggestions: this.getSuggestions(value)
        });
    };

    render() {
        const { value, suggestions } = this.state;

        // Autosuggest will pass through all these props to the input.
        const inputProps = {
            placeholder: 'Type a label',
            value,
            onChange: this.onChange,
            autoFocus: true
        };

        return (
            <Autosuggest
                suggestions={suggestions}
                shouldRenderSuggestions={shouldRenderSuggestions}
                onSuggestionsFetchRequested={this.onSuggestionsFetchRequested}
                onSuggestionsClearRequested={() => {}}
                getSuggestionValue={getSuggestionValue}
                renderSuggestion={renderSuggestion}
                inputProps={inputProps}
            />
        );
    }
}

export {AutoCompleter}