import { Input } from 'antd';

const { TextArea } = Input;

type QuestionInputProps = {
  value: string;
  onChange: (value: string) => void;
};

export const QuestionInput = (props: QuestionInputProps) => {
    return (
        <TextArea
            rows={3}
            placeholder="Введите свой запрос..."
            value={props.value}
            onChange={(event) => props.onChange(event.target.value)}
        />
    )
}