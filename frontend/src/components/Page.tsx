// root
import {Card, notification} from 'antd';
import {QuestionButton} from "./QuestionButton.tsx";
import {QuestionInput} from "./QuestionInput.tsx";
import {UploadButton} from "./UploadButton.tsx";
import { AnswerField } from "./AnswerField.tsx";
import {useState} from "react";
import {handleQuestionSubmit} from "../handlers/handleQuestionSubmit.ts";
import {uploadLibrary} from "../handlers/handleLibraryUpload.ts";
import './Page.css';

export const Page = () => {
    // чат
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [notificationApi, contextHolder] = notification.useNotification({
        placement: 'topRight',
        maxCount: 3,
    });

    // загрузка
    const [uploading, setUploading] = useState(false);

    const handleQuestion = async () => {
        notificationApi.destroy('question-error');
        await handleQuestionSubmit(question, setLoading, setAnswer, (description) => {
            notificationApi.error({
                key: 'question-error',
                title: 'Не удалось подобрать книги',
                description,
                duration: description.length > 160 || description.includes('\n') ? 0 : 10,
            });
        });
    };

    const handleFileSelected = async (file: File) => {
        if (uploading) return;
        setUploading(true);
        notificationApi.destroy('library-upload');

        try {
            const description = await uploadLibrary(file);
            notificationApi.success({
                key: 'library-upload',
                title: 'Каталог обработан',
                description,
                duration: 4,
            });
        } catch (error: unknown) {
            notificationApi.error({
                key: 'library-upload',
                title: 'Каталог не загружен',
                description: error instanceof Error ? error.message : 'Не удалось загрузить файл.',
                duration: 0,
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <>
        {contextHolder}
        <div className="bookclub-page">
            <Card
                className="bookclub-card"
                title={'Добро пожаловать в книжную лавку "Цогл!"'}
            >
                <div className="bookclub-content">
                    <AnswerField answer={answer}/>
                    <div className="question-form">
                        <QuestionInput value={question} onChange={setQuestion}/>
                        <div className="question-form__actions">
                            <QuestionButton
                                onClick={handleQuestion}
                                loading={loading}
                                disabled={loading /*|| !question.trim()*/}
                            />
                            <UploadButton
                                className="bookclub-upload-button"
                                uploading={uploading}
                                onFileSelected={handleFileSelected}
                            />
                        </div>
                    </div>
                </div>
            </Card>
        </div>
        </>
    )
}
