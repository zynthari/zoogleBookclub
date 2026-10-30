import { Button } from 'antd';

type QuestionButtonProps = {
    onClick: () => void | Promise<void>;
    loading: boolean,
    disabled: boolean
};

export const QuestionButton = (props: QuestionButtonProps) => {
    return (
        <Button
            color="cyan"
            variant="filled"
            onClick={props.onClick}
            loading={props.loading}
            disabled={props.disabled}
        >
            Запросить книги
        </Button>
    )
}
