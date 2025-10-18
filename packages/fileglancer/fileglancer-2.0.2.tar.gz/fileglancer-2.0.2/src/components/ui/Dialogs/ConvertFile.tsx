import React from 'react';
import { Button, Typography } from '@material-tailwind/react';
import toast from 'react-hot-toast';

import FgDialog from './FgDialog';
import TextWithFilePath from './TextWithFilePath';
import { Spinner } from '@/components/ui/widgets/Loaders';
import useConvertFileDialog from '@/hooks/useConvertFileDialog';
import { usePreferencesContext } from '@/contexts/PreferencesContext';
import { useFileBrowserContext } from '@/contexts/FileBrowserContext';
import { useTicketContext } from '@/contexts/TicketsContext';
import { getPreferredPathForDisplay } from '@/utils/pathHandling';

type ItemNamingDialogProps = {
  readonly showConvertFileDialog: boolean;
  readonly setShowConvertFileDialog: React.Dispatch<
    React.SetStateAction<boolean>
  >;
};

export default function ConvertFileDialog({
  showConvertFileDialog,
  setShowConvertFileDialog
}: ItemNamingDialogProps): JSX.Element {
  const [waitingForTicketResponse, setWaitingForTicketResponse] =
    React.useState(false);
  const { destinationFolder, setDestinationFolder, handleTicketSubmit } =
    useConvertFileDialog();
  const { pathPreference } = usePreferencesContext();
  const { fileBrowserState } = useFileBrowserContext();
  const { refreshTickets } = useTicketContext();

  const placeholderText =
    pathPreference[0] === 'windows_path'
      ? '\\path\\to\\destination\\folder\\'
      : '/path/to/destination/folder/';

  const displayPath = getPreferredPathForDisplay(
    pathPreference,
    fileBrowserState.currentFileSharePath,
    fileBrowserState.propertiesTarget?.path
  );

  return (
    <FgDialog
      onClose={() => setShowConvertFileDialog(false)}
      open={showConvertFileDialog}
    >
      <Typography
        className="mb-4 text-foreground font-bold text-2xl"
        variant="h4"
      >
        Convert images to OME-Zarr format
      </Typography>
      <Typography className="my-4 text-large text-foreground">
        This form will create a new request for Scientific Computing to convert
        the image data at this path to OME-Zarr format, suitable for viewing in
        external viewers like Neuroglancer.
      </Typography>
      <form
        onSubmit={async event => {
          event.preventDefault();
          setWaitingForTicketResponse(true);
          const createTicketResult = await handleTicketSubmit();

          if (!createTicketResult.success) {
            toast.error(`Error creating ticket: ${createTicketResult.error}`);
            setWaitingForTicketResponse(false);
          } else {
            const refreshTicketResponse = await refreshTickets();
            toast.success('Ticket created!');
            setWaitingForTicketResponse(false);
            if (!refreshTicketResponse.success) {
              toast.error(
                `Error refreshing ticket list: ${refreshTicketResponse.error}`
              );
            }
          }
          setShowConvertFileDialog(false);
        }}
      >
        <TextWithFilePath path={displayPath} text="Source Folder" />
        <div className="flex flex-col gap-2 my-4">
          <Typography
            as="label"
            className="text-foreground font-semibold"
            htmlFor="destination_folder"
          >
            Destination Folder
          </Typography>
          <input
            autoFocus
            className="mb-4 p-2 text-foreground text-lg border border-primary-light rounded-sm focus:outline-none focus:border-primary bg-background"
            id="destination_folder"
            onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
              setDestinationFolder(event.target.value);
            }}
            placeholder={placeholderText}
            type="text"
            value={destinationFolder}
          />
        </div>
        <Button
          className="!rounded-md"
          disabled={!destinationFolder}
          type="submit"
        >
          {waitingForTicketResponse ? (
            <Spinner customClasses="border-white" text="Processing..." />
          ) : (
            'Submit'
          )}
        </Button>
      </form>
    </FgDialog>
  );
}
