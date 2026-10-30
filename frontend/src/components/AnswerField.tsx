import Markdown from 'react-markdown';
import './AnswerField.css';

type AnswerFieldProps = {
  answer: string;
};

export const AnswerField = ({ answer }: AnswerFieldProps) => {
    return (
        <div className="answer">
            <Markdown>{answer || "Тут скоро появится рекомендация =)"}</Markdown>
        </div>
    )
}
